# 网易云音乐无损解析

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/Suxiaoqinx/Netease_url?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/Suxiaoqinx/Netease_url?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/Suxiaoqinx/Netease_url?style=flat-square)
![GitHub license](https://img.shields.io/github/license/Suxiaoqinx/Netease_url?style=flat-square)

**功能强大的网易云音乐解析工具**

支持歌曲搜索 | 单曲解析 | 歌单解析 | 专辑解析 | 音乐下载

[在线体验](https://wyapi.toubiec.cn) • [使用文档](./使用文档.md) • [问题反馈](https://github.com/Suxiaoqinx/Netease_url/issues)

</div>

---

> **⚠️ 重要声明**  
> 本项目采用 MIT 许可证开源。根据 MIT 许可证的条款，任何个人或组织均可自由使用、修改和分发本项目的源代码，包括用于商业项目。

**注意**：本项目旨在为开源社区做贡献，我们鼓励用户：
- 在遵守开源精神的前提下使用和分享代码
- 如有改进，欢迎贡献回本项目
- 在商业使用中，请考虑对开源项目的支持和回馈

虽然 MIT 许可证允许商业使用，但我们希望用户能尊重开源精神，合理使用本项目。

## ✨ 功能特性

### 🎵 核心功能
- **🔍 歌曲搜索**：支持关键词搜索网易云音乐库中的歌曲
- **📝 歌名批量匹配**：粘贴歌名或上传 TXT，获取最相关歌曲 ID 和链接后直接批量解析
- **🎧 单曲解析**：解析单首歌曲的详细信息和下载链接
- **📋 歌单解析**：批量解析歌单中的所有歌曲信息
- **💿 专辑解析**：批量解析专辑中的所有歌曲信息
- **⬇️ 音乐下载**：支持多种音质的音乐文件下载

### 🎼 音质支持
- `standard`：标准音质 (128kbps)
- `exhigh`：极高音质 (320kbps)
- `lossless`：无损音质 (FLAC)
- `hires`：Hi-Res音质 (24bit/96kHz)
- `jyeffect`：高清环绕声
- `sky`：沉浸环绕声
- `jymaster`：超清母带

### 🌐 使用方式
- **Web界面**：直观友好的网页操作界面
- **RESTful API**：完整的API接口支持
- **批量处理**：支持歌单和专辑的批量解析
- **多格式支持**：支持ID和链接多种输入格式

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- 网易云音乐黑胶会员账号

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/Suxiaoqinx/Netease_url.git
cd Netease_url
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置Cookie
在 `cookie.txt` 文件中填入黑胶会员账号的Cookie：

> 💡 **获取Cookie方法**：登录网易云音乐网页版 → F12开发者工具 → Network标签页 → 复制任意请求的Cookie值


> 杜比全景声音质需要设备支持，不同的设备可能会返回不同码率的 url cookie 需要传入os=pc保证返回正常码率的 url

#### 4. 启动服务
```bash
python main.py
```

#### 5. 访问界面
打开浏览器访问：`http://localhost:5000`

### 🐳 Docker部署

```bash
# 使用Docker Compose
docker-compose up -d

# 或使用Docker
docker build -t netease-music-api .
docker run -d -p 5000:5000 netease-music-api
```

---

## 📖 使用指南

### Web界面使用

#### 🔍 歌曲搜索
1. 选择功能：**歌曲搜索**
2. 输入关键词（歌曲名、歌手名等）
3. 点击**搜索**按钮
4. 在搜索结果中点击**解析**或**下载**按钮

#### 🎧 单曲解析
1. 选择功能：**单曲解析**
2. 输入歌曲ID或网易云音乐链接
   - 支持格式：`1234567890` 或 `https://music.163.com/song?id=1234567890`
3. 点击**解析**按钮查看歌曲信息

#### 📁 文件批量解析与下载
1. 打开首页的**批量任务**，选择**我已有 ID 或链接**
2. 选择解析音质，直接粘贴歌曲 ID/链接，或上传 `.txt`、`.csv`、`.xlsx` 文件；两种输入可以同时使用
3. TXT/CSV 每行填写一个歌曲 ID 或网易云单曲链接；Excel 使用“歌曲 ID”或“网易云链接”列
4. 点击**开始解析**，页面会自动完成识别和资源解析
5. 解析完成后点击**下载全部可用歌曲**，服务会将音频和处理结果打包为 ZIP

批量上传会按出现顺序自动去重。单个文件最大 10MB、最多识别 2000 首歌曲，每批最多处理 200 首，超过后自动分批。TXT/CSV 支持 UTF-8、GB18030 编码。

#### 📝 按歌名查找后批量解析
1. 在首页的**批量任务**中选择**我只有歌曲名称**，每行输入一个歌曲名称，或上传每行一个名称的 `.txt` 文件
2. 建议写成“歌名 | 歌手”，例如 `晴天 | 周杰伦`，可提高匹配准确率
3. 点击**查找并自动解析**，系统会查找歌曲 ID/链接，并自动解析匹配可靠的歌曲
4. 如果存在同名或歌手不一致的歌曲，可展开候选卡片切换版本，再点击**解析已确认歌曲**
5. 解析完成后直接点击**下载全部可用歌曲**下载 ZIP

一次最多查找 200 个歌曲名称。系统默认取每个名称最相关的一首；只有需要人工判断的结果才会暂停等待确认，未找到的名称会单独显示。

#### 📋 歌单解析
1. 选择功能：**歌单解析**
2. 输入歌单ID或网易云音乐歌单链接
   - 支持格式：`1234567890` 或 `https://music.163.com/playlist?id=1234567890`
3. 点击**解析**按钮查看歌单中所有歌曲
4. 点击单首歌曲的**解析**或**下载**按钮

#### 💿 专辑解析
1. 选择功能：**专辑解析**
2. 输入专辑ID或网易云音乐专辑链接
   - 支持格式：`1234567890` 或 `https://music.163.com/album?id=1234567890`
3. 点击**解析**按钮查看专辑中所有歌曲
4. 点击单首歌曲的**解析**或**下载**按钮

#### ⬇️ 音乐下载
1. 选择功能：**音乐下载**
2. 输入歌曲ID或链接
3. 选择音质（标准/极高/无损/Hi-Res等）
4. 点击**下载**按钮

### 支持的链接格式

```
# 歌曲链接
https://music.163.com/song?id=1234567890
https://music.163.com/#/song?id=1234567890

# 歌单链接
https://music.163.com/playlist?id=1234567890
https://music.163.com/#/playlist?id=1234567890

# 专辑链接
https://music.163.com/album?id=1234567890
https://music.163.com/#/album?id=1234567890

# 直接使用ID
1234567890
```

## 🔌 API接口文档

### 基础信息
- **Base URL**: `http://localhost:5000`
- **请求方式**: GET / POST
- **响应格式**: JSON

### 接口列表

#### 1. 健康检查
```http
GET /health
```
**响应示例**:
```json
{
  "status": "ok",
  "message": "Service is running"
}
```

#### 2. 歌曲搜索
```http
POST /search
Content-Type: application/json

{
  "keywords": "周杰伦 稻香",
  "limit": 10
}
```
**响应示例**:
```json
{
  "code": 200,
  "result": {
    "songs": [
      {
        "id": 185668,
        "name": "稻香",
        "artists": ["周杰伦"],
        "album": "魔杰座",
        "duration": 223000
      }
    ]
  }
}
```

#### 3. 单曲解析
```http
POST /song
Content-Type: application/json

{
  "id": "185668"
}
```

#### 4. 歌单解析
```http
POST /playlist
Content-Type: application/json

{
  "id": "123456789"
}
```

#### 5. 专辑解析
```http
POST /album
Content-Type: application/json

{
  "id": "123456789"
}
```

#### 6. 音乐下载
```http
POST /download
Content-Type: application/json

{
  "id": "185668",
  "quality": "lossless"
}
```
**响应**: 直接返回音频文件流

#### 7. 批量歌名查找
```http
POST /batch/resolve-names
Content-Type: application/json

{
  "queries": ["晴天 | 周杰伦", "海阔天空 | Beyond"]
}
```

也可使用 `multipart/form-data` 上传 `.txt` 文件，并通过 `content` 字段同时提交手工输入的歌名。响应包含匹配歌曲的 ID、网易云链接和未找到明细。

#### 8. 文件批量解析
```http
POST /batch/parse
Content-Type: multipart/form-data

file: songs.xlsx
content: 185668\nhttps://music.163.com/song?id=1392990601
level: lossless
```

`file` 支持 TXT、CSV、XLSX；Excel 需包含“歌曲 ID”或“网易云链接”表头。`content` 为可选的手工粘贴内容，可以和文件同时提交。

也可以直接提交 JSON：

```json
{
  "ids": ["185668", "1392990601"],
  "level": "lossless"
}
```

#### 9. 批量下载 ZIP
```http
POST /batch/download
Content-Type: application/json

{
  "ids": ["185668", "1392990601"],
  "quality": "lossless"
}
```

成功时返回 ZIP 文件。部分歌曲失败不会中断整个批次，失败明细会写入 ZIP 中的 `批量下载结果.txt`。

---

## 音质参数说明（仅限单曲解析）

- `standard`：标准音质
- `exhigh`：极高音质
- `lossless`：无损音质
- `hires`：Hi-Res音质
- `jyeffect`：高清环绕声
- `sky`：沉浸环绕声
- `jymaster`：超清母带

> 黑胶VIP音质：standard, exhigh, lossless, hires, jyeffect  
> 黑胶SVIP音质：sky, jymaster

---

## Docker 一键部署

1. **修改参数**

   - 如需修改端口，请编辑 `.env` 或 `docker-compose.yml` 文件中的 `ports` 配置，例如：

     ```yaml
     ports:
       - "8080:5000"
     ```

2. **启动服务**

   ```bash
   docker-compose up -d
   ```

---

## 在线演示

[在线解析](https://wyapi.toubiec.cn/)

---

## 注意事项

- 必须使用黑胶会员账号的 Cookie 才能解析高音质资源。
- Cookie 格式请严格按照 `cookie.txt` 示例填写。

---

## 致谢

- [Ravizhan](https://github.com/ravizhan)

---

## 反馈与交流

- 在 Github [Issues](https://github.com/Suxiaoqinx/Netease_url/issues) 提交反馈
- 或访问 [我的博客](https://www.toubiec.cn)

---

欢迎 Star、Fork 和 PR！

