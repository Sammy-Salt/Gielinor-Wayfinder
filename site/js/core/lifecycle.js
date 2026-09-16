import { Logger } from "./logger.js";
export async function runPage(Page){
  const page=typeof Page==="function"?new Page():Page;
  try { await page.init?.(); await page.load?.(); await page.render?.(); await page.bindEvents?.(); return page; }
  catch(error){ Logger.error("Page lifecycle failed",error); page.error?.(error); return null; }
}
export function pageController({init,load,render,bindEvents,error}={}){ return {init,load,render,bindEvents,error}; }
