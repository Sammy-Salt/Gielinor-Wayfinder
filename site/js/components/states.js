import { createTextElement } from "../core/utils.js";
export function stateMessage(text, className="empty"){ return createTextElement("div",text,className); }
export function renderState(container,{loading="Loading…",empty="Nothing found.",error="Unable to load data.",hasData=true,failed=false}={}){
  if(!container)return; container.replaceChildren(stateMessage(failed?error:(hasData?loading:empty),failed?"error":(hasData?"loading":"empty")));
}
