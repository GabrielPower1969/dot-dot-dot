// 快手创作者平台 发布. verified: null.
export default {
  platform: "kuaishou", login_url: "https://cp.kuaishou.com/article/publish/video", verified: null,
  steps: [
    { goto: "https://cp.kuaishou.com/article/publish/video" }, { wait: 3000 },
    { upload: ["css=input[type=file]", "text=上传视频"], file: "{video}" },
    { waitFor: ["placeholder=添加合适的话题和描述", "css=#work-description-edit", "css=textarea"], timeout: 90000 }, { wait: 2000 },
    { type: ["css=#work-description-edit", "placeholder=添加合适的话题和描述", "css=textarea"], value: "{title} {hashtags}" },
    { click: ["text=上传封面", "text=编辑封面"], optional: true }, { upload: ["css=input[type=file][accept*=image]"], file: "{cover}", optional: true }, { click: ["text=确定", "role=button name=^完成$"], optional: true },
    { click: ["text=定时发布", "role=radio name=定时发布"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^发布$", "text=发布"] },
  ],
};
