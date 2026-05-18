# 前端接口对接文档

本文档面向前端调用方，接口信息基于当前 FastAPI 代码整理。

## 1. 基础约定

### 1.1 Base URL

本地开发默认接口前缀：

```text
/api/v1
```

示例：

```text
GET /api/v1/health/status
```

### 1.2 数据格式

除登录接口外，接口请求体和响应体均使用 JSON。

```http
Content-Type: application/json
```

登录接口使用 OAuth2 表单格式：

```http
Content-Type: application/x-www-form-urlencoded
```

### 1.3 时间格式

时间字段使用 ISO 8601 字符串，由后端返回，例如：

```json
"2026-05-18T10:20:30.123456Z"
```

前端提交 `due_date` 时也建议使用 ISO 8601：

```json
"2026-05-20T18:00:00+08:00"
```

### 1.4 认证方式

除健康检查、注册、登录外，其余接口均需要 Bearer Token。

```http
Authorization: Bearer <access_token>
```

Token 从登录接口 `/api/v1/auth/login` 获取。

### 1.5 通用错误

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `401` | 未登录、Token 无效、用户不可用 | `{"detail":"Could not validate credentials"}` |
| `403` | 无权限访问项目或操作任务 | `{"detail":"Not a project member"}` |
| `404` | 项目、任务或用户不存在 | `{"detail":"Project not found"}` |
| `422` | 请求参数校验失败 | FastAPI 默认校验错误结构 |

注意：部分业务错误的 `detail` 是字符串，部分是对象，前端展示时建议兼容两种格式。

## 2. 快速前端封装示例

### 2.1 fetch 封装

```ts
const API_BASE = "/api/v1";

function getToken() {
  return localStorage.getItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();

  if (!response.ok) {
    throw data;
  }

  return data as T;
}
```

### 2.2 登录示例

```ts
async function login(username: string, password: string) {
  const form = new URLSearchParams();
  form.set("username", username);
  form.set("password", password);

  const response = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
  });

  const data = await response.json();

  if (!response.ok) {
    throw data;
  }

  localStorage.setItem("access_token", data.access_token);
  return data;
}
```

## 3. 数据模型

### 3.1 User

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 是 | 用户 ID |
| `email` | `string` | 是 | 邮箱 |
| `username` | `string` | 是 | 用户名 |
| `is_active` | `boolean` | 是 | 是否可用 |
| `created_at` | `string` | 是 | 创建时间 |

### 3.2 Token

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `access_token` | `string` | 是 | 访问令牌 |
| `token_type` | `string` | 是 | 固定为 `bearer` |

### 3.3 Project

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 是 | 项目 ID |
| `name` | `string` | 是 | 项目名称 |
| `description` | `string \| null` | 否 | 项目描述 |
| `owner_id` | `number` | 是 | 项目拥有者用户 ID |
| `created_at` | `string` | 是 | 创建时间 |
| `updated_at` | `string` | 是 | 更新时间 |
| `task_count` | `number` | 是 | 项目下任务数量 |

### 3.4 Task

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 是 | 任务 ID |
| `title` | `string` | 是 | 任务标题 |
| `description` | `string \| null` | 否 | 任务描述 |
| `status` | `TaskStatus` | 是 | 任务状态 |
| `priority` | `TaskPriority` | 是 | 优先级 |
| `due_date` | `string \| null` | 否 | 截止时间 |
| `project_id` | `number` | 是 | 所属项目 ID |
| `creator_id` | `number` | 是 | 创建人用户 ID |
| `assignee_id` | `number \| null` | 否 | 负责人用户 ID |
| `created_at` | `string` | 是 | 创建时间 |
| `updated_at` | `string` | 是 | 更新时间 |

### 3.5 枚举值

任务状态 `TaskStatus`：

```ts
type TaskStatus = "todo" | "in_progress" | "review" | "done" | "canceled";
```

任务优先级 `TaskPriority`：

```ts
type TaskPriority = "low" | "medium" | "high" | "urgent";
```

## 4. 健康检查

### GET /health/status

检查服务是否可用。

认证：不需要

请求：

```http
GET /api/v1/health/status
```

响应 `200`：

```json
{
  "status": "ok"
}
```

## 5. 认证接口

### POST /auth/register

注册账号。

认证：不需要

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `email` | `string` | 是 | 邮箱，需符合邮箱格式 |
| `username` | `string` | 是 | 用户名，需唯一 |
| `password` | `string` | 是 | 密码 |

请求示例：

```json
{
  "email": "alice@example.com",
  "username": "alice",
  "password": "secret123"
}
```

响应 `201`：`User`

```json
{
  "id": 1,
  "email": "alice@example.com",
  "username": "alice",
  "is_active": true,
  "created_at": "2026-05-18T10:20:30.123456Z"
}
```

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `400` | 邮箱已注册 | `{"detail":{"msg":"Email already registered"}}` |
| `400` | 用户名已注册 | `{"detail":{"msg":"Username already registered"}}` |

### POST /auth/login

登录账号并获取 Token。

认证：不需要

请求体：`application/x-www-form-urlencoded`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `username` | `string` | 是 | 用户名，不是邮箱 |
| `password` | `string` | 是 | 密码 |

请求示例：

```bash
curl -X POST "/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

响应 `200`：`Token`

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `401` | 用户名或密码错误 | `{"detail":{"msg":"Invalid username or password"}}` |

## 6. 用户接口

### GET /user/me

获取当前登录用户信息。

认证：需要

请求：

```http
GET /api/v1/user/me
Authorization: Bearer <access_token>
```

响应 `200`：`User`

### GET /user/list

获取用户列表，通常用于选择项目成员或任务负责人。

认证：需要

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `skip` | `number` | 否 | `0` | 跳过数量 |
| `limit` | `number` | 否 | `20` | 返回数量 |

请求示例：

```http
GET /api/v1/user/list?skip=0&limit=20
Authorization: Bearer <access_token>
```

响应 `200`：`User[]`

```json
[
  {
    "id": 1,
    "email": "alice@example.com",
    "username": "alice",
    "is_active": true,
    "created_at": "2026-05-18T10:20:30.123456Z"
  }
]
```

## 7. 项目接口

### GET /projects/

获取当前用户参与的项目列表。

认证：需要

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `skip` | `number` | 否 | `0` | 跳过数量 |
| `limit` | `number` | 否 | `20` | 返回数量 |

请求示例：

```http
GET /api/v1/projects/?skip=0&limit=20
Authorization: Bearer <access_token>
```

响应 `200`：`Project[]`

### GET /projects/{project_id}

获取项目详情。

认证：需要；当前用户必须是项目成员。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `project_id` | `number` | 项目 ID |

响应 `200`：`Project`

常见错误：

| 状态码 | 场景 |
| --- | --- |
| `403` | 当前用户不是项目成员 |
| `404` | 项目不存在 |

### POST /projects/

创建项目。

认证：需要

创建成功后，当前用户会自动成为该项目 owner。

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 | 项目名称 |
| `description` | `string \| null` | 否 | 项目描述 |

请求示例：

```json
{
  "name": "Roadmap",
  "description": "Q2 execution"
}
```

响应 `201`：`Project`

```json
{
  "id": 1,
  "name": "Roadmap",
  "description": "Q2 execution",
  "owner_id": 1,
  "created_at": "2026-05-18T10:20:30.123456Z",
  "updated_at": "2026-05-18T10:20:30.123456Z",
  "task_count": 0
}
```

### PUT /projects/{project_id}

更新项目信息。

认证：需要；只有项目 owner 可以操作。

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string \| null` | 否 | 项目名称 |
| `description` | `string \| null` | 否 | 项目描述 |

请求示例：

```json
{
  "name": "Roadmap v2",
  "description": "Q2 and Q3 execution"
}
```

响应 `200`：`Project`

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `403` | 当前用户不是 owner | `{"detail":"Only project owner can do this"}` |
| `404` | 项目不存在 | `{"detail":"Project not found"}` |

### DELETE /projects/{project_id}

删除项目。

认证：需要；只有项目 owner 可以操作。

响应：`204 No Content`

注意：删除项目会同时删除项目成员关系；任务表外键配置了级联删除。

### POST /projects/{project_id}/members

添加项目成员。

认证：需要；只有项目 owner 可以操作。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `project_id` | `number` | 项目 ID |

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_list` | `number[]` | 是 | 用户 ID 列表，至少 1 个 |

请求示例：

```json
{
  "user_list": [2, 3]
}
```

响应 `201`：

```json
{
  "added_user_ids": [2, 3],
  "skipped_user_ids": []
}
```

说明：

- 后端会自动去重。
- 已经在项目中的用户不会重复添加，会出现在 `skipped_user_ids`。
- 如果存在无效用户 ID，整个请求返回 `404`。

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `404` | 用户不存在 | `{"detail":{"msg":"用户不存在","user_ids":[999]}}` |
| `403` | 当前用户不是 owner | `{"detail":"Only project owner can do this"}` |

### GET /projects/{project_id}/members

查看项目成员。

认证：需要；当前用户必须是项目成员。

响应 `200`：`User[]`

```json
[
  {
    "id": 1,
    "email": "alice@example.com",
    "username": "alice",
    "is_active": true,
    "created_at": "2026-05-18T10:20:30.123456Z"
  }
]
```

## 8. 任务接口

### GET /tasks

获取当前用户参与项目内的任务列表。

认证：需要

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `status` | `TaskStatus` | 否 | 无 | 按任务状态筛选 |
| `skip` | `number` | 否 | `0` | 跳过数量 |
| `limit` | `number` | 否 | `10` | 返回数量 |

请求示例：

```http
GET /api/v1/tasks?status=todo&skip=0&limit=10
Authorization: Bearer <access_token>
```

响应 `200`：`Task[]`

### GET /tasks/{id}

获取任务详情。

认证：需要；当前用户必须是任务所属项目成员。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 任务 ID |

响应 `200`：`Task`

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `404` | 任务不存在 | `{"detail":{"msg":"没找到任务"}}` |
| `403` | 当前用户不是项目成员 | `{"detail":"Not a project member"}` |

### POST /tasks

创建任务。

认证：需要；当前用户必须是项目成员。如果指定 `assignee_id`，负责人也必须是项目成员。

请求体：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | `string` | 是 | 无 | 任务标题，长度 1-20 |
| `description` | `string \| null` | 否 | `null` | 任务描述 |
| `status` | `TaskStatus` | 否 | `todo` | 任务状态 |
| `project_id` | `number` | 是 | 无 | 所属项目 ID |
| `priority` | `TaskPriority` | 否 | `medium` | 优先级 |
| `due_date` | `string \| null` | 否 | `null` | 截止时间 |
| `assignee_id` | `number \| null` | 否 | `null` | 负责人用户 ID |

请求示例：

```json
{
  "title": "Design API",
  "description": "Draft task endpoints",
  "status": "todo",
  "project_id": 1,
  "priority": "high",
  "due_date": "2026-05-20T18:00:00+08:00",
  "assignee_id": 2
}
```

响应 `200`：`Task`

```json
{
  "id": 1,
  "title": "Design API",
  "description": "Draft task endpoints",
  "status": "todo",
  "priority": "high",
  "due_date": "2026-05-20T10:00:00Z",
  "project_id": 1,
  "creator_id": 1,
  "assignee_id": 2,
  "created_at": "2026-05-18T10:20:30.123456Z",
  "updated_at": "2026-05-18T10:20:30.123456Z"
}
```

常见错误：

| 状态码 | 场景 |
| --- | --- |
| `403` | 当前用户不是项目成员 |
| `403` | `assignee_id` 对应用户不是项目成员 |
| `404` | 项目不存在 |
| `422` | `title` 超长、枚举值错误等参数校验失败 |

### PUT /tasks/{task_id}

更新任务。

认证：需要；只有项目 owner 或任务创建者可以操作。如果指定 `assignee_id`，负责人必须是项目成员。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `task_id` | `number` | 任务 ID |

请求体：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | `string \| null` | 否 | 不变 | 任务标题，长度 1-200 |
| `description` | `string \| null` | 否 | 不变 | 任务描述 |
| `status` | `TaskStatus \| null` | 否 | 不变 | 任务状态 |
| `priority` | `TaskPriority` | 否 | 不变 | 优先级 |
| `due_date` | `string \| null` | 否 | 不变 | 截止时间；传 `null` 可清空 |
| `assignee_id` | `number \| null` | 否 | 不变 | 负责人；传 `null` 可清空 |

请求示例：

```json
{
  "title": "Design API v2",
  "status": "in_progress",
  "priority": "urgent"
}
```

响应 `200`：`Task`

常见错误：

| 状态码 | 场景 | 响应示例 |
| --- | --- | --- |
| `403` | 不是项目 owner 或任务创建者 | `{"detail":{"msg":"只有项目拥有者或任务创建者可以操作"}}` |
| `404` | 任务不存在 | `{"detail":{"msg":"没找到任务"}}` |
| `422` | 参数校验失败 | FastAPI 默认校验错误结构 |

### DELETE /tasks/{task_id}

删除任务。

认证：需要；只有项目 owner 或任务创建者可以操作。

响应：`204 No Content`

注意：后端当前虽然返回了 `{"detail":"删除成功"}`，但状态码是 `204`，HTTP 规范下前端应按无响应体处理。

## 9. 推荐前端类型定义

```ts
export type TaskStatus =
  | "todo"
  | "in_progress"
  | "review"
  | "done"
  | "canceled";

export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: "bearer";
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
  task_count: number;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  project_id: number;
  creator_id: number;
  assignee_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string | null;
}

export interface UpdateProjectPayload {
  name?: string | null;
  description?: string | null;
}

export interface CreateTaskPayload {
  title: string;
  description?: string | null;
  status?: TaskStatus;
  project_id: number;
  priority?: TaskPriority;
  due_date?: string | null;
  assignee_id?: number | null;
}

export interface UpdateTaskPayload {
  title?: string | null;
  description?: string | null;
  status?: TaskStatus | null;
  priority?: TaskPriority;
  due_date?: string | null;
  assignee_id?: number | null;
}
```

## 10. 前端接入注意事项

- 登录接口必须用 `application/x-www-form-urlencoded`，不要用 JSON。
- 登录字段是 `username`，不是 `email`。
- 注册、登录、健康检查不需要 Token，其余接口都需要 Token。
- 项目成员权限会影响项目详情、成员列表、任务列表和任务详情可见范围。
- 创建或更新任务时，如果传入 `assignee_id`，该用户必须已经被加入对应项目。
- 删除接口返回 `204`，前端不要强制解析 JSON。
- 当前后端未在 `app/main.py` 中配置 CORS；如果前端和后端不同域名或端口，需要后端补充 CORS 配置。
