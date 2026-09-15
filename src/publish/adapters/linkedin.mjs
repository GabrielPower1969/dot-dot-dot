// LinkedIn feed post with video, scheduled via the clock icon. verified: null.
export default {
  platform: "linkedin", login_url: "https://www.linkedin.com/feed/", verified: null,
  steps: [
    { goto: "https://www.linkedin.com/feed/" }, { wait: 3000 },
    { click: ["role=button name=Start a post", "text=Start a post"] }, { wait: 1500 },
    { click: ["role=button name=Add media", "role=button name=Add a video", "css=button[aria-label*='media']"] },
    { upload: ["css=input[type=file]"], file: "{video}" }, { wait: 3000 },
    { click: ["role=button name=^Next$", "role=button name=^Done$"], optional: true },
    { type: ["role=textbox name=Text editor", "css=.ql-editor", "css=[contenteditable=true]"], value: "{body}\n\n{hashtags}" },
    { click: ["role=button name=Schedule post", "css=button[aria-label*='Schedule']"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^Schedule$", "role=button name=^Post$", "role=button name=^Next$"] },
  ],
};
