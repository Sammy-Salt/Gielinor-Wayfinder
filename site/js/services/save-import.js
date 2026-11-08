/**
 * 2009Scape save import with optional File System Access re-read.
 *
 * Manual pick stores a normalized snapshot and (when supported) a file handle.
 * On later app opens we try to re-read the same file; otherwise we reuse the
 * last successful snapshot so Character / Progress / Crafting stay populated.
 */
import { Storage } from '../core/storage.js';
import { OSRSSync } from './player-sync.js';

const META_KEY = 'gielinorSaveImportMeta';
const SNAPSHOT_KEY = 'gielinorSaveImportSnapshot';
const HANDLE_DB = 'gielinor-wayfinder';
const HANDLE_STORE = 'file-handles';
const HANDLE_KEY = 'player-save';

const SKILL_NAMES = [
  'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic',
  'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting',
  'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer', 'Farming',
  'Runecrafting', 'Hunter', 'Construction', 'Summoning'
];

function nowIso() {
  return new Date().toISOString();
}

function openHandleDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(HANDLE_DB, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(HANDLE_STORE)) db.createObjectStore(HANDLE_STORE);
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error || new Error('IndexedDB open failed'));
  });
}

async function idbGet(key) {
  const db = await openHandleDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(HANDLE_STORE, 'readonly');
    const req = tx.objectStore(HANDLE_STORE).get(key);
    req.onsuccess = () => resolve(req.result ?? null);
    req.onerror = () => reject(req.error || new Error('IndexedDB get failed'));
  });
}

async function idbSet(key, value) {
  const db = await openHandleDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(HANDLE_STORE, 'readwrite');
    tx.objectStore(HANDLE_STORE).put(value, key);
    tx.oncomplete = () => resolve(true);
    tx.onerror = () => reject(tx.error || new Error('IndexedDB put failed'));
  });
}

async function idbDelete(key) {
  const db = await openHandleDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(HANDLE_STORE, 'readwrite');
    tx.objectStore(HANDLE_STORE).delete(key);
    tx.oncomplete = () => resolve(true);
    tx.onerror = () => reject(tx.error || new Error('IndexedDB delete failed'));
  });
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') return Object.values(value);
  return [];
}

function itemRows(source) {
  return asArray(source)
    .map((row, index) => {
      if (row == null) return null;
      if (typeof row === 'number') {
        const id = Number(row);
        return id > 0 ? { id, amount: 1, slot: index, charge: 1000 } : null;
      }
      if (typeof row !== 'object') return null;
      const id = Number(row.id ?? row.itemId ?? row.item ?? -1);
      const amount = Number(row.amount ?? row.quantity ?? row.count ?? 0);
      if (!Number.isFinite(id) || id < 0 || !Number.isFinite(amount) || amount <= 0) return null;
      return {
        id,
        amount,
        slot: Number(row.slot ?? index) || index,
        charge: Number(row.charge ?? 1000) || 1000
      };
    })
    .filter(Boolean);
}

function skillNameFromId(id) {
  const n = Number(id);
  return SKILL_NAMES[n] || `Skill ${n}`;
}

function normalizeSkills(raw) {
  const rows = asArray(raw);
  if (!rows.length) return [];
  return rows.map((row, index) => {
    if (!row || typeof row !== 'object') return null;
    const id = Number(row.id ?? index);
    const name = String(row.name || skillNameFromId(id)).trim() || skillNameFromId(id);
    const level = Math.max(1, Number(row.level ?? row.static ?? row.staticLevel ?? 1) || 1);
    const dynamicLevel = Math.max(1, Number(row.dynamicLevel ?? row.dynamic ?? level) || level);
    const xp = Math.max(0, Number(row.xp ?? row.experience ?? 0) || 0);
    return { id, name, level, dynamicLevel, xp };
  }).filter(Boolean);
}

function normalizeQuests(raw, questPoints) {
  const items = asArray(raw?.items ?? raw?.quests ?? raw)
    .map((row, index) => {
      if (!row || typeof row !== 'object') return null;
      const name = String(row.name ?? row.title ?? `Quest ${row.id ?? index}`).trim();
      if (!name) return null;
      const stage = Number(row.stage ?? row.state ?? 0) || 0;
      const completed = row.completed === true || stage >= 100;
      return {
        id: Number(row.id ?? index) || index,
        name,
        stage,
        completed
      };
    })
    .filter(Boolean);
  const completedCount = items.filter(q => q.completed).length;
  return {
    totalTracked: items.length,
    completed: completedCount,
    questPoints: Math.max(0, Number(questPoints ?? raw?.questPoints ?? 0) || 0),
    items
  };
}

function isNormalizedSnapshot(obj) {
  return obj
    && typeof obj === 'object'
    && Number(obj.formatVersion) === 2
    && obj.player
    && Array.isArray(obj.skills);
}

/**
 * Convert either a shipped player-sync snapshot or a raw-ish 2009Scape JSON save
 * into the formatVersion 2 contract consumed by OSRSSync.
 */
export function normalizeSave(raw, meta = {}) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('Save file is not a JSON object');
  }

  if (isNormalizedSnapshot(raw)) {
    const copy = structuredClone(raw);
    copy.source = {
      ...(copy.source || {}),
      character: copy.source?.character || meta.fileName || 'Imported save',
      readOnly: true,
      syncedAt: nowIso(),
      importMode: 'normalized'
    };
    return OSRSSync.validateSnapshot(copy);
  }

  // Raw / near-raw 2009Scape player JSON (PlayerSaver style).
  const skills = normalizeSkills(raw.skills ?? raw.skillData ?? raw.Skills);
  if (!skills.length) throw new Error('Save file has no recognizable skills data');

  const inventory = itemRows(raw.inventory ?? raw.Inventory);
  const equipment = itemRows(raw.equipment ?? raw.Equipment);
  const bank = itemRows(raw.bank ?? raw.Bank ?? raw.bankData);

  const locationSrc = raw.location || raw.Location || {};
  const location = {
    x: Number(locationSrc.x ?? raw.x ?? 0) || 0,
    y: Number(locationSrc.y ?? raw.y ?? 0) || 0,
    plane: Number(locationSrc.plane ?? locationSrc.z ?? raw.plane ?? 0) || 0
  };

  const totalXP = skills.reduce((n, s) => n + Number(s.xp || 0), 0);
  const quests = normalizeQuests(raw.quests ?? raw.questData, raw.questPoints ?? raw.player?.questPoints);

  const playerName = String(
    raw.username
    || raw.name
    || raw.displayName
    || raw.player?.name
    || meta.fileName?.replace(/\.json$/i, '')
    || 'Player'
  ).slice(0, 120);

  const snapshot = {
    formatVersion: 2,
    source: {
      character: playerName,
      sourceVersion: Number(raw.version ?? raw.saveVersion ?? 0) || null,
      readOnly: true,
      syncedAt: nowIso(),
      importMode: 'raw-2009scape',
      fileName: meta.fileName || null
    },
    metadata: {
      saveVersion: Number(raw.version ?? raw.saveVersion ?? 0) || null
    },
    player: {
      name: playerName,
      totalXP,
      questPoints: quests.questPoints,
      location,
      spellbook: Number(raw.spellbook ?? raw.spellBook ?? raw.player?.spellbook ?? 0) || 0,
      runEnergy: Number(raw.runEnergy ?? raw.settings?.runEnergy ?? 100) || 0,
      specialEnergy: Number(raw.specialEnergy ?? raw.settings?.specialEnergy ?? 100) || 0,
      lifepoints: Number(raw.lifepoints ?? raw.hitpoints ?? raw.player?.lifepoints ?? skills.find(s => s.name === 'Hitpoints')?.dynamicLevel ?? 10) || 10,
      prayerPoints: Number(raw.prayerPoints ?? raw.player?.prayerPoints ?? skills.find(s => s.name === 'Prayer')?.dynamicLevel ?? 1) || 0
    },
    skills,
    quests,
    inventory,
    equipment,
    bank,
    location,
    slayer: raw.slayer && typeof raw.slayer === 'object' ? raw.slayer : {},
    achievementDiaries: asArray(raw.achievementDiaries ?? raw.diaries),
    statistics: raw.statistics && typeof raw.statistics === 'object' ? raw.statistics : {}
  };

  return OSRSSync.validateSnapshot(snapshot);
}

export function getImportMeta() {
  return Storage.jsonGet(META_KEY, null);
}

export function getCachedSnapshot() {
  const snap = Storage.jsonGet(SNAPSHOT_KEY, null);
  if (!snap) return null;
  try {
    return OSRSSync.validateSnapshot(snap);
  } catch {
    return null;
  }
}

function setCachedSnapshot(snapshot, meta) {
  Storage.jsonSet(SNAPSHOT_KEY, snapshot);
  Storage.jsonSet(META_KEY, meta);
}

export async function clearImport() {
  Storage.remove(SNAPSHOT_KEY);
  Storage.remove(META_KEY);
  try { await idbDelete(HANDLE_KEY); } catch { /* ignore */ }
  return true;
}

async function ensureHandlePermission(handle, mode = 'read') {
  if (!handle?.queryPermission || !handle?.requestPermission) return false;
  let state = await handle.queryPermission({ mode });
  if (state === 'granted') return true;
  if (state === 'prompt') {
    state = await handle.requestPermission({ mode });
    return state === 'granted';
  }
  return false;
}

async function readFileAsJson(file) {
  const text = await file.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error('Selected file is not valid JSON');
  }
  return data;
}

/**
 * Import from a user-picked File (fallback path without persistent handle).
 */
export async function importFromFile(file) {
  if (!file) throw new Error('No file selected');
  const raw = await readFileAsJson(file);
  const snapshot = normalizeSave(raw, { fileName: file.name });
  const meta = {
    fileName: file.name,
    fileSize: file.size,
    importedAt: nowIso(),
    hasHandle: false,
    mode: snapshot.source?.importMode || 'file'
  };
  setCachedSnapshot(snapshot, meta);
  OSRSSync.applyExternalSnapshot(snapshot);
  return { snapshot, meta };
}

/**
 * Import via File System Access API and remember the handle for later re-reads.
 */
export async function importWithFilePicker() {
  if (typeof window.showOpenFilePicker === 'function') {
    const [handle] = await window.showOpenFilePicker({
      multiple: false,
      types: [{
        description: '2009Scape save / player JSON',
        accept: { 'application/json': ['.json'] }
      }],
      excludeAcceptAllOption: false
    });
    const file = await handle.getFile();
    const raw = await readFileAsJson(file);
    const snapshot = normalizeSave(raw, { fileName: file.name });
    try { await idbSet(HANDLE_KEY, handle); } catch { /* private mode etc. */ }
    const meta = {
      fileName: file.name,
      fileSize: file.size,
      importedAt: nowIso(),
      hasHandle: true,
      mode: snapshot.source?.importMode || 'file'
    };
    setCachedSnapshot(snapshot, meta);
    OSRSSync.applyExternalSnapshot(snapshot);
    return { snapshot, meta };
  }

  // Fallback: classic input element
  return new Promise((resolve, reject) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json,.json';
    input.onchange = async () => {
      try {
        const file = input.files?.[0];
        if (!file) return reject(new Error('No file selected'));
        resolve(await importFromFile(file));
      } catch (error) {
        reject(error);
      }
    };
    input.click();
  });
}

/**
 * Try to re-read the remembered file handle; otherwise return cached snapshot.
 */
export async function loadRememberedSave({ forceFileRead = true } = {}) {
  const cached = getCachedSnapshot();
  const meta = getImportMeta();

  if (forceFileRead) {
    try {
      const handle = await idbGet(HANDLE_KEY);
      if (handle) {
        const allowed = await ensureHandlePermission(handle, 'read');
        if (allowed) {
          const file = await handle.getFile();
          const raw = await readFileAsJson(file);
          const snapshot = normalizeSave(raw, { fileName: file.name || meta?.fileName });
          const nextMeta = {
            fileName: file.name || meta?.fileName || 'save.json',
            fileSize: file.size,
            importedAt: nowIso(),
            hasHandle: true,
            mode: snapshot.source?.importMode || 'file',
            reloadedFromHandle: true
          };
          setCachedSnapshot(snapshot, nextMeta);
          OSRSSync.applyExternalSnapshot(snapshot);
          return { snapshot, meta: nextMeta, source: 'handle' };
        }
      }
    } catch (error) {
      console.warn('[Gielinor Wayfinder] remembered save re-read failed', error);
    }
  }

  if (cached) {
    OSRSSync.applyExternalSnapshot(cached);
    return { snapshot: cached, meta, source: 'cache' };
  }

  return null;
}

export const SaveImport = {
  normalizeSave,
  getImportMeta,
  getCachedSnapshot,
  clearImport,
  importFromFile,
  importWithFilePicker,
  loadRememberedSave
};
