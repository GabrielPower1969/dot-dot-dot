// TikTok Studio upload. verified: null.
export default {
  platform: "tiktok", login_url: "https://www.tiktok.com/tiktokstudio/upload", verified: null,
  steps: [
    { goto: "https://www.tiktok.com/tiktokstudio/upload" }, { wait: 3000 },
    { upload: ["css=input[type=file]", "text=Select video"], file: "{video}" },
    { waitFor: ["css=.public-DraftEditor-content", "css=[contenteditable=true]", "label=Description"], timeout: 90000 }, { wait: 2000 },
    { type: ["css=.public-DraftEditor-content", "css=[contenteditable=true]", "label=Description"], value: "{title} {hashtags}" },
    { click: ["text=Edit cover", "text=Cover"], optional: true }, { click: ["text=Upload cover", "role=tab name=Upload"], optional: true },
    { upload: ["css=input[type=file][accept*=image]"], file: "{cover}", optional: true }, { click: ["role=button name=^Confirm$", "text=Confirm"], optional: true },
    { check: ["role=radio name=Schedule", "text=Schedule"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^Schedule$", "role=button name=^Post$", "text=Post"] },
  ],
};
