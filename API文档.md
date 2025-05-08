# 个性化旅游系统 API 文档

本文档详细描述了个性化旅游系统的API端点、请求参数和响应格式。系统的API分为以下几个主要部分：用户认证、景点管理和地图服务。

## 目录

- [用户认证](#用户认证)
  - [登录](#登录)
  - [游客登录](#游客登录)
  - [会话检查](#会话检查)
  - [登出](#登出)
  - [注册](#注册)
- [景点服务](#景点服务)
  - [推荐景点](#推荐景点)
  - [搜索景点](#搜索景点)
- [地图服务](#地图服务)
  - [查看景点地图](#查看景点地图)
  - [获取周边景点](#获取周边景点)
  - [获取兴趣点(POI)](#获取兴趣点poi)
  - [按关键词获取兴趣点](#按关键词获取兴趣点)
  - [路线导航](#路线导航)

## 用户认证

### 登录

处理用户登录请求。

- **URL:** `/api/login`
- **方法:** `POST`
- **请求类型:** JSON
- **请求参数:**
  - `username` (字符串): 用户名
  - `password` (字符串): 密码

**请求示例:**
```json
{
    "username": "example_user",
    "password": "example_password"
}
```

**成功响应 (200 OK):**
```json
{
    "success": true,
    "message": "登录成功"
}
```
成功登录后，会在响应中设置一个名为 `user_session` 的HTTPOnly Cookie，有效期为30分钟。

**失败响应 (401 Unauthorized):**
```json
{
    "success": false,
    "message": "用户名或密码错误"
}
```

### 游客登录

创建一个临时的游客账户，并为其创建会话和设置cookie。

- **URL:** `/api/guest-login`
- **方法:** `POST`
- **请求类型:** JSON
- **请求参数:** 无

**成功响应 (200 OK):**
```json
{
    "success": true,
    "message": "游客登录成功",
    "user": {
        "username": "guest_xxxxxxxx" // 随机生成的游客用户名
    }
}
```
成功登录后，会在响应中设置一个名为 `user_session` 的HTTPOnly Cookie，有效期为1小时。

**失败响应 (400 Bad Request):**
```json
{
    "success": false,
    "message": "游客登录失败"
}
```

### 会话检查

检查当前是否存在有效的用户会话。

- **URL:** `/api/check-session`
- **方法:** `GET`
- **请求参数:** 无 (依赖 `user_session` Cookie 进行验证)
- **认证:** 需要用户登录

**成功响应 (200 OK, 会话有效):**
```json
{
    "success": true,
    "message": "会话有效",
    "user": {
        "username": "current_username"
    }
}
```

**失败响应 (401 Unauthorized, 会话无效或未登录):**
```json
{
    "success": false,
    "message": "请先登录"
}
```

### 登出

处理用户登出请求，清除服务器端的会话信息并删除客户端的会话cookie。

- **URL:** `/api/logout`
- **方法:** `GET`, `POST`
- **请求参数:** 无 (依赖 `user_session` Cookie)

**成功响应 (200 OK):**
```json
{
    "success": true,
    "message": "已成功登出"
}
```
成功登出后，会删除名为 `user_session` 的Cookie。

### 注册

处理用户注册请求，接收用户名、密码和兴趣标签，创建新用户。

- **URL:** `/api/register`
- **方法:** `POST`
- **请求类型:** JSON
- **请求参数:**
  - `username` (字符串): 用户希望注册的用户名
  - `password` (字符串): 用户设置的密码
  - `selectedTags` (字符串数组): 用户选择的兴趣标签列表

**请求示例:**
```json
{
    "username": "new_user",
    "password": "secure_password",
    "selectedTags": ["自然风光", "历史遗迹", "美食"]
}
```

**成功响应 (200 OK):**
```json
{
    "success": true,
    "message": "注册成功"
}
```

**失败响应:**

- **400 Bad Request (无效输入):**
```json
{
    "success": false,
    "message": "无效的请求数据" 
}
```
或
```json
{
    "success": false,
    "message": "缺少必要的注册信息"
}
```
或
```json
{
    "success": false,
    "message": "兴趣标签格式错误"
}
```

- **409 Conflict (用户名已存在):**
```json
{
    "success": false,
    "message": "注册失败，用户名可能已存在"
}
```

## 景点服务

### 推荐景点

根据当前登录用户的兴趣标签返回推荐的景点列表。

- **URL:** `/api/recommended-spots`
- **方法:** `GET`
- **请求参数:** 无 (依赖 `user_session` Cookie 进行用户识别)
- **认证:** 需要用户登录

**成功响应 (200 OK):**
```json
{
    "success": true,
    "spots": [
        {
            "name": "景点名称",
            "id": "景点ID",
            "score": 4.5,
            "type": "景点类型",
            "visited_time": 100,
            "img": "image_url.jpg"
        },
        // ...更多景点对象
    ]
}
```
如果用户没有对应的推荐或推荐列表为空，`spots` 数组可能为空。

**失败响应 (401 Unauthorized, 未登录):**
```json
{
    "success": false,
    "message": "请先登录"
}
```

### 搜索景点

根据用户输入的关键词、景点类型和排序方式搜索景点。

- **URL:** `/api/search-spots`
- **方法:** `GET`
- **请求参数:**
  - `keyword` (字符串, 可选): 用于搜索景点名称的关键词
  - `type` (字符串, 可选): 用于筛选特定类型的景点
  - `sort_by` (字符串, 可选, 默认值: 'default'): 排序依据
    - 可选值: 'default' (默认排序), 'popularity_desc' (按热度降序)
- **认证:** 需要用户登录

**请求示例:**
```
/api/search-spots?keyword=古城&type=历史遗迹&sort_by=popularity_desc
```

**成功响应 (200 OK):**
```json
{
    "success": true,
    "spots": [
        {
            "name": "景点名称",
            "id": "景点ID",
            "score": 4.5,
            "type": "景点类型",
            "visited_time": 120,
            "img": "image_url.jpg"
        },
        // ...更多景点对象
    ]
}
```
如果未找到匹配的景点，`spots` 数组可能为空。

**失败响应 (401 Unauthorized, 未登录):**
```json
{
    "success": false,
    "message": "请先登录"
}
```

## 地图服务

### 查看景点地图

显示指定景点的地图页面。

- **URL:** `/map/<int:spot_id>`
- **方法:** `GET`
- **URL 参数:**
  - `spot_id` (整数): 要显示的景点的ID
- **认证:** 需要用户登录

**行为:**
- 根据 `spot_id` 获取景点信息
- 如果景点不存在，返回 404 错误
- 如果景点位置信息格式不正确，返回 400 错误
- 渲染 `map.html` 模板，并传递景点ID、纬度、经度和景点详细信息

### 获取周边景点

获取指定景点周边的其他景点数据(POI - Points of Interest)。

- **URL:** `/map/<int:spot_id>/api/scenicSpots`
- **方法:** `GET`
- **URL 参数:**
  - `spot_id` (整数): 中心景点的ID
- **认证:** 需要用户登录

**成功响应 (200 OK):**
```json
{
    "pois": [
        {
            "name": "周边景点A",
            "location": "纬度,经度",
            // ...其他POI属性
        },
        // ...更多POI
    ]
}
```

**失败响应:**

- **404 Not Found:** 如果中心景点不存在或位置信息缺失
```json
{"error": "Spot not found"}
```
或
```json
{"error": "Spot location not found"}
```

- **500 Internal Server Error:** 如果获取POI数据失败
```json
{"error": "Failed to fetch POI data"}
```

### 获取兴趣点(POI)

根据指定位置获取所有类型的兴趣点(POI)数据，并进行合并排序。

- **URL:** `/map/api/poi/<location>`
- **方法:** `GET`
- **URL 参数:**
  - `location` (字符串): 中心位置的坐标，格式通常为 "纬度,经度"

**行为:**
- 从配置文件获取所有POI类型
- 对每种POI类型，调用 `map_module.get_POI_reversal` 获取半径500米内的POI列表
- 使用 `merge_sort` 合并所有类型的POI列表
- 将合并后的列表反转（可能是为了按距离或其他标准降序排列）

**成功响应 (200 OK):**
```json
[
    {
        "name": "POI 名称",
        "distance": "距离", // 或其他排序依据的字段
        // ...其他POI属性
    },
    // ...更多POI对象，已合并排序和反转
]
```
如果获取过程中出现问题或没有POI，可能返回空列表 `[]`。

### 按关键词获取兴趣点

根据指定位置和关键词（POI类型）获取兴趣点(POI)数据。

- **URL:** `/map/api/poi/<location>/<keyword>`
- **方法:** `GET`
- **URL 参数:**
  - `location` (字符串): 中心位置的坐标，格式通常为 "纬度,经度"
  - `keyword` (字符串): POI的类型或关键词

**行为:**
- 调用 `map_module.get_POI_reversal` 获取指定关键词和位置（半径500米内）的POI列表
- 将获取的POI列表反转

**成功响应 (200 OK):**
```json
[
    {
        "name": "POI 名称",
        // ...其他POI属性
    },
    // ...更多POI对象，已反转
]
```
如果获取过程中出现问题或没有匹配的POI，可能返回空列表 `[]`。

### 路线导航

获取两点或多点之间的导航路线规划数据。

- **URL:** `/map/api/navigation`
- **方法:** `POST`
- **请求类型:** JSON
- **请求体参数:**
```json
{
    "points": [
        {"lat": 纬度1, "lng": 经度1}, // 起点
        {"lat": 纬度2, "lng": 经度2}, // 终点或途径点
        // ...更多途径点
    ]
}
```

**成功响应 (200 OK):**
```json
{
    "success": true,
    "route": [
        [纬度A, 经度A], // 路径点1
        [纬度B, 经度B], // 路径点2
        // ...更多路径点坐标
    ],
    "distance": 总距离, // 单位：米
    "duration": null // 预计时间（秒），当前版本可能未实现或固定为null
}
```

**失败响应:**

- **400 Bad Request:** 如果输入数据无效（如缺少 `points`，坐标点少于2个，或坐标点格式错误）
```json
{"success": false, "message": "无效的输入数据"}
```
或
```json
{"success": false, "message": "无效的坐标点数据，至少需要两个点"}
```
或
```json
{"success": false, "message": "坐标点格式错误，应为 {lat: number, lng: number}"}
```

- **500 Internal Server Error:** 如果路线规划过程中发生内部错误（如地图模块规划失败）
```json
{"success": false, "message": "路线规划失败: <具体错误信息>"}
```

## 认证说明

大多数API端点需要用户登录才能访问。登录后，服务器会设置一个名为 `user_session` 的HTTPOnly Cookie。该Cookie将在后续请求中用于验证用户身份。

如果请求一个需要认证的API端点但没有有效的会话，将返回401状态码和以下JSON响应:
```json
{
    "success": false,
    "message": "请先登录"
}
```

对于页面路由，未认证的请求会被重定向到登录页面。
