# SC6113 个人作业提交清单

代码主体已经齐全，但以下步骤必须用你本人的 MetaMask、GitHub 和 Render 账户完成，不能代填或伪造。

## 一、你提交前必须完成的 6 件事

1. **在 Sepolia 部署合约**：按 README 的 Remix 方法部署 `contracts/GoalSave.sol`。
2. **记录链上信息**：保存合约地址、部署交易哈希和部署区块号；写入 `deployment.json`。
3. **上传 GitHub**：建立你自己的仓库并上传本项目，确认 `.env` 没有被上传。
4. **部署 Render**：连接 GitHub 仓库，设置 `CONTRACT_ADDRESS`、`DEPLOYMENT_BLOCK` 和 `CHAIN_ID=11155111`。
5. **做一次完整演示并截图**：创建目标、充值、错误输入、锁定提款、成功提款、Etherscan 记录、Render 页面。
6. **更新报告**：填写姓名/学号/链接，把真实截图放入报告，删除所有 `TO BE COMPLETED` 标记后导出最终 PDF。

## 二、推荐演示数据

- 目标名称：`Professional Course Fund`
- 目标金额：`0.02 ETH`
- 第一次充值：`0.01 ETH`
- 第二次充值：`0.01 ETH`
- 截止时间：当前时间后 7 天

用很小的 Sepolia 测试币即可，不要使用主网或真实 ETH。

## 三、交付文件核对

- [ ] `.sol`：`contracts/GoalSave.sol`
- [ ] ABI：`abi/GoalSave.json`
- [ ] Flask：`app.py`
- [ ] HTML：`templates/index.html`
- [ ] CSS：`static/styles.css`
- [ ] JavaScript：`static/app.js`
- [ ] Render link：已写进 README 和报告
- [ ] GitHub link：已写进 README 和报告
- [ ] Sepolia contract address：已写进 README 和报告
- [ ] 5–8 页 PDF 报告：信息和截图均为最终版本
- [ ] 自动测试截图或测试输出
- [ ] README 部署/运行说明

## 四、答辩时要能解释的内容

- 为什么 `msg.value` 才是真正收到的 ETH，而不是用户自己输入的 `_amount`。
- 为什么提款前先把 `savedAmount` 设为 0，再调用外部地址（checks-effects-interactions）。
- 为什么只有 goal owner 可以提款。
- 普通提款的解锁条件：达到 target 或经过 deadline。
- `emergencyWithdraw` 与普通提款有什么区别，为什么使用不同事件记录。
- ABI 在 JavaScript 与 Solidity 合约之间起什么作用。
- Flask 做了什么：页面托管、配置/ABI、输入验证和可选的交易回执查询。
- Render 托管的是 Web 应用；合约运行在 Sepolia，两者不是同一个部署。

## 五、学术诚信提醒

本项目没有复制同学仓库的业务代码，但你仍应逐个文件阅读、运行并能说明自己的选择。老师课堂示例只作为技术路线参考；报告中已经明确说明参考来源与本项目的新增设计。
