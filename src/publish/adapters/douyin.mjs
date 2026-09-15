// 抖音创作者中心 发布视频. verified: null.
export default {
  platform: "douyin", login_url: "https://creator.douyin.com/creator-micro/content/upload", verified: null,
  steps: [
    { goto: "https://creator.douyin.com/creator-micro/content/upload" }, { wait: 3000 },
    { upload: ["css=input[type=file]", "text=上传视频"], file: "{video}" },
    { waitFor: ["placeholder=填写作品标题", "css=input.semi-input"], timeout: 90000 }, { wait: 2000 },
    { fill: ["placeholder=填写作品标题", "css=input.semi-input"], value: "{title}" },
    { type: ["css=.editor-kit-container", "css=[data-placeholder*=作品简介]", "placeholder=添加作品简介"], value: "{body} {hashtags}", optional: true },
    { click: ["text=选择封面", "text=设置封面"], optional: true }, { click: ["text=上传封面", "role=tab name=上传封面"], optional: true },
    { upload: ["css=input[type=file][accept*=image]"], file: "{cover}", optional: true }, { click: ["role=button name=^完成$", "text=完成"], optional: true },
    { click: ["text=定时发布", "role=radio name=定时发布"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^发布$", "text=发布"] },
  ],
};
