// 小红书创作服务平台 发布视频. verified: null. 标题 ≤ 20 字.
export default {
  platform: "xiaohongshu", login_url: "https://creator.xiaohongshu.com/publish/publish", verified: null,
  steps: [
    { goto: "https://creator.xiaohongshu.com/publish/publish" }, { wait: 3000 },
    { click: ["text=上传视频", "role=tab name=上传视频"], optional: true },
    { upload: ["css=input[type=file]", "text=选择视频"], file: "{video}" },
    { waitFor: ["placeholder=填写标题", "css=input.d-text"], timeout: 90000 }, { wait: 2000 },
    { fill: ["placeholder=填写标题", "css=input.d-text"], value: "{title}" },
    { type: ["css=#post-textarea", "css=.ql-editor", "placeholder=输入正文描述"], value: "{body}\n{hashtags}", optional: true },
    { click: ["text=设置封面", "text=编辑封面"], optional: true }, { click: ["text=上传封面", "text=本地上传"], optional: true },
    { upload: ["css=input[type=file][accept*=image]", "css=.cover-upload input"], file: "{cover}", optional: true },
    { click: ["role=button name=^完成$", "text=确定"], optional: true },
    { click: ["text=定时发布", "css=.el-switch"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^发布$", "text=发布", "text=定时发布"] },
  ],
};
