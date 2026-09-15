// B站 创作中心 投稿. verified: null. Cover: B站 auto-generates; custom cover via 更改封面 → 上传封面.
export default {
  platform: "bilibili", login_url: "https://member.bilibili.com/platform/upload/video/frame", verified: null,
  steps: [
    { goto: "https://member.bilibili.com/platform/upload/video/frame" }, { wait: 3000 },
    { upload: ["css=input[type=file]", "text=上传视频"], file: "{video}" },
    { waitFor: ["placeholder=请输入稿件标题", "css=input.input-val"], timeout: 60000 }, { wait: 2000 },
    { fill: ["placeholder=请输入稿件标题", "css=input.input-val"], value: "{title}" },
    { click: ["text=更改封面", "text=编辑封面"], optional: true }, { click: ["text=上传封面"], optional: true },
    { upload: ["css=input[type=file][accept*=image]", "css=.cover-upload input[type=file]"], file: "{cover}", optional: true },
    { click: ["role=button name=^完成$", "text=完成"], optional: true },
    { type: ["css=.ql-editor", "placeholder=填写更全面的相关信息", "css=textarea"], value: "{body}", optional: true },
    { type: ["placeholder=按回车键Enter创建标签", "css=.tag-input input"], value: "{tag1}", optional: true }, { press: "Enter" },
    { click: ["text=定时发布", "role=checkbox name=定时发布"], optional: true }, { shot: "form" },
    { submit: ["role=button name=^立即投稿$", "text=立即投稿", "text=定时投稿"] },
  ],
};
