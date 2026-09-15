// YouTube Studio web upload. verified: null (steps written from the 2025–26 Studio layout; first run will tell).
export default {
  platform: "youtube", login_url: "https://studio.youtube.com", verified: null,
  steps: [
    { goto: "https://studio.youtube.com" }, { wait: 2500 },
    { click: ["role=button name=^Create$", "css=#create-icon", "text=Create"] },
    { click: ["text=Upload videos", "role=menuitem name=Upload"] },
    { upload: ["css=input[type=file]", "text=Select files"], file: "{video}" },
    { waitFor: ["css=#textbox", "label=Add a title"], timeout: 30000 }, { wait: 3000 },
    { type: ["css=#title-textarea #textbox", "css=ytcp-social-suggestions-textbox#title-textarea #textbox", "label=Add a title"], value: "{title}" },
    { type: ["css=#description-textarea #textbox", "label=Tell viewers about your video"], value: "{body}\n\n{hashtags}", optional: true },
    { upload: ["css=#file-loader", "css=input#file-loader", "text=Upload thumbnail", "text=Upload file"], file: "{cover}", optional: true },
    { check: ["role=radio name=No, it's not made for kids", "css=tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]"], optional: true },
    { shot: "details" },
    { click: ["role=button name=^Next$", "css=#next-button"] }, { click: ["role=button name=^Next$", "css=#next-button"] }, { click: ["role=button name=^Next$", "css=#next-button"] },
    { check: ["role=radio name=Schedule", "css=tp-yt-paper-radio-button[name=SCHEDULE]"] },
    { click: ["css=#datepicker-trigger", "role=button name=date"], optional: true }, { type: ["css=#datepicker-trigger input", "css=tp-yt-paper-input#datepicker input"], value: "{date_en}", optional: true }, { press: "Enter" },
    { type: ["css=#time-of-day-trigger input", "css=#time-of-day input", "role=combobox name=time"], value: "{time_hm}", optional: true }, { press: "Enter" },
    { shot: "visibility" },
    { submit: ["role=button name=^Schedule$", "css=#done-button", "role=button name=^Publish$"] },
  ],
};
