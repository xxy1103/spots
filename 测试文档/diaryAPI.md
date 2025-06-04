## 日记模块API文档

### 1. 获取用户日记列表

**路径：** `/diary/user/<int:user_id>`
**方法：** `GET`
**权限：** 需要登录
**功能：** 获取指定用户的所有日记列表

**请求参数：**

* [user_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（路径参数）：用户ID，整数类型

**响应：**

* 成功：返回 `user_diaries.html` 页面，包含用户信息和日记列表
* 失败：返回 `error.html` 页面，显示错误信息（例如"用户不存在"）

**示例响应：**

**返回HTML页面，包含日记列表和用户信息**

* []()
* []()
* []()
* []()

### 2. 获取日记详情

**路径：** `/diary/<int:diary_id>`
**方法：** `GET`
**权限：** 需要登录
**功能：** 获取指定日记的详细信息

**请求参数：**

* [diary_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（路径参数）：日记ID，整数类型

**响应：**

* 成功：返回 `diary_detail.html` 页面，包含日记详细信息和作者信息
* 失败：返回 `error.html` 页面，显示错误信息（例如"日记不存在"或"用户不存在"）

**额外操作：**

* 每次查看都会增加日记的访问次数（[visited_time](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)）

### 3. 删除日记

**路径：** `/diary/<int:diary_id>`
**方法：** `DELETE` 或 `POST`（带有 `_method=DELETE`参数）
**权限：** 需要登录，且只有日记作者可以删除
**功能：** 删除指定的日记

**请求参数：**

* [diary_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（路径参数）：日记ID，整数类型
* `_method` （POST 请求时需要）：值为 "DELETE"，用于模拟DELETE请求

**响应：**

* 成功：重定向到用户日记列表页面
* 失败：返回 `error.html` 页面，显示错误信息（例如"日记不存在"或"无权限删除该日记"）

**额外操作：**

* 从日记管理器中删除日记
* 更新对应景点评分
* 从用户记录中删除日记引用

### 4. 获取日记推荐

**路径：** `/diary/recommend/user/<int:user_id>`
**方法：** `GET`
**权限：** 需要登录
**功能：** 获取为指定用户推荐的日记

**请求参数：**

* [user_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（路径参数）：用户ID，整数类型
* [topK](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（查询参数，可选）：返回推荐数量，默认为10

**响应：**

* 成功：JSON格式的推荐日记列表
* 失败：返回 `error.html` 页面，显示错误信息（例如"用户不存在或推荐内容为空"或"未找到推荐内容"）

**示例响应：**

**[**

**  **{

**    **"id"**: **1**,**

**    **"title"**: **"日记标题"**,**

**    **"user_id"**: **123**,**

**    **"spot_id"**: **456**,**

**    **"time"**: **"2025-05-24"**,**

**    **"score"**: **4.5**,**

**    **"visited_time"**: **10**,**

**    **"img_list"**: **[**"路径1"**, **"路径2"**]**,**

**    **"video_path"**: **[**"路径1"**]**,**

**    **"scoreToSpot"**: **4.8

**  **}**,**

**  **...

**]**


### 5. 添加日记（提交）

**路径：** `/diary/add`
**方法：** `POST`
**权限：** 需要登录
**功能：** 添加新的日记

**请求参数：**

* [spot_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（表单参数）：景点ID，整数类型
* [spot_marking](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（表单参数，可选）：对景点的评分，范围0-5，默认为0
* [title](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（表单参数）：日记标题
* [content](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（表单参数）：日记内容
* [images](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（文件参数，可选）：日记的图片文件，可多个
* [videos](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（文件参数，可选）：日记的视频文件，可多个

**响应：**

* 成功：重定向到新创建的日记详情页面
* 失败：返回 `error.html` 页面，显示错误信息（例如"请填写完整信息"或"添加日记失败"）

**额外操作：**

* 上传的图片和视频会被保存到对应景点的目录下
* 更新景点的评分
* 将日记添加到用户的日记列表中

### 6. 添加日记（页面）

**路径：** `/diary/add`
**方法：** `GET`
**权限：** 需要登录
**功能：** 显示添加日记的页面

**请求参数：** 无

**响应：**

* 成功：返回 `diary_add.html` 页面，包含所有景点信息供选择

### 7. 对日记进行评分

**路径：** `/diary/<int:diary_id>/marking`
**方法：** `POST`
**权限：** 需要登录
**功能：** 为指定的日记添加评分

**请求参数：**

* [diary_id](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（路径参数）：日记ID，整数类型
* [score](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（表单参数）：评分值，浮点数，范围0-5

**响应：**

* 成功：重定向到日记详情页面
* 失败：返回 `error.html` 页面，显示错误信息（例如"评分必须大于0小于等于5"）

**额外操作：**

* 更新用户的评分记录
* 更新日记索引和评分信息

### 8. 搜索日记

**路径：** `/diary/search`
**方法：** `GET`
**权限：** 需要登录
**功能：** 根据关键字搜索日记

**请求参数：**

* [keyword](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（查询参数，可选）：搜索关键字，默认为空字符串
* [type](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（查询参数，可选）：搜索类型，可选值有：
  * [title](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)：按标题搜索（默认）
  * [content](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)：按内容搜索
  * [user](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)：按用户搜索
  * [spot](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)：按景点搜索
  * 其他值：综合搜索（全部方式）
* [sort_by](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)（查询参数，可选）：排序方式，可选值：
  * `value1`：按评分排序（默认）
  * `value2`：按访问量排序（热度）

**响应：**

* 成功：返回 `diary_search.html` 页面，包含搜索结果和搜索关键字

**特性：**

* 如果关键字为空，返回所有日记
* 搜索结果根据指定的排序方式（评分或热度）进行排序

**示例响应：**

**返回HTML页面，包含排序后的日记列表**

* 返回HTML页面，包含排序后的日记列表

---

以上就是 [routes.py](vscode-file://vscode-app/d:/ProgramData/Microsoft%20VS%20Code%20Insiders/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 中所有API的详细文档。每个API都包括路径、方法、权限要求、功能描述、请求参数和响应信息。这些文档可以帮助开发者和用户更好地理解和使用日记模块的功能。
