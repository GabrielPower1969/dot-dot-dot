// Instagram Reels via Meta Business Suite composer (schedules; personal instagram.com has no scheduler). verified: null.
export default {
  platform: "instagram", login_url: "https://business.facebook.com/latest/reels_composer", verified: null,
  steps: [
    { goto: "https://business.facebook.com/latest/reels_composer" }, { wait: 4000 },
    { upload: ["css=input[type=file]", "text=Add video"], file: "{video}" },
    { waitFor: ["role=textbox name=Description", "css=[contenteditable=true]"], timeout: 90000 }, { wait: 2000 },
    { type: ["role=textbox name=Description", "css=[contenteditable=true]"], value: "{title}\n{body}\n{hashtags}" },
    { click: ["text=Scheduling options", "text=Schedule"], optional: true }, { check: ["role=radio name=Schedule", "role=switch name=Schedule"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^Schedule$", "role=button name=^Share$", "role=button name=^Publish$"] },
  ],
};
