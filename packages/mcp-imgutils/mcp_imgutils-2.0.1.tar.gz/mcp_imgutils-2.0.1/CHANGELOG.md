## [2.0.1](https://github.com/donghao1393/mcp-imgutils/compare/v2.0.0...v2.0.1) (2025-08-02)


### Bug Fixes

* 修复重构后的CI失败问题 ([#4](https://github.com/donghao1393/mcp-imgutils/issues/4)) ([9c90162](https://github.com/donghao1393/mcp-imgutils/commit/9c9016271bea6019a64bd4135f56069ebf73cabf))

# [2.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.4...v2.0.0) (2025-08-02)


### Code Refactoring

* 完全重构项目结构以对齐dbutils模式 ([01e92ab](https://github.com/donghao1393/mcp-imgutils/commit/01e92ab737c588454cf361375613f1a6f597a3b4))


### BREAKING CHANGES

* 重构包结构和入口点

- 重命名包目录: src/imgutils/ → src/mcp_imgutils/
- 更新入口点: mcp-imgutils = "mcp_imgutils:main"
- 重构主函数: 将__main__.py逻辑移到__init__.py中的main()函数
- 更新构建配置: packages = ["src/mcp_imgutils"]
- 修复所有测试文件中的导入路径

现在完全对齐dbutils的项目结构:
- 包名: mcp-imgutils (PyPI, 连字符)
- 源码: src/mcp_imgutils/ (下划线)
- 可执行文件: mcp-imgutils (连字符)
- 入口点: mcp_imgutils:main (下划线)

这解决了uvx兼容性问题，现在uvx mcp-imgutils可以正常工作

## [1.4.4](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.3...v1.4.4) (2025-08-02)


### Bug Fixes

* 修复可执行文件名称不匹配问题 ([58fb85d](https://github.com/donghao1393/mcp-imgutils/commit/58fb85d8a741b8a40e2fe6daee73fc625ed3f8f6))

## [1.4.3](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.2...v1.4.3) (2025-08-02)


### Bug Fixes

* 修复PyPI构建失败问题 ([2b67ecc](https://github.com/donghao1393/mcp-imgutils/commit/2b67ecc1139b7e99bb1e04986d893f0eb20d3567))

## [1.4.2](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.1...v1.4.2) (2025-08-02)


### Bug Fixes

* 修复PyPI项目名称不匹配问题 ([fb2b57a](https://github.com/donghao1393/mcp-imgutils/commit/fb2b57a401dd67aee0fdc3ff700ed5653c66c438))

## [1.4.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.0...v1.4.1) (2025-08-02)


### Bug Fixes

* 修复文档中关于MCP配置的错误 ([204a362](https://github.com/donghao1393/mcp-imgutils/commit/204a362f6eac06b41301ee95f6859b0878e245d1))

# [1.4.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.3.0...v1.4.0) (2025-08-02)


### Features

* 添加EXIF元数据支持 ([#3](https://github.com/donghao1393/mcp-imgutils/issues/3)) ([dae9d09](https://github.com/donghao1393/mcp-imgutils/commit/dae9d09e0f5b73fe446e5bae999b1a105155d04b)), closes [#2](https://github.com/donghao1393/mcp-imgutils/issues/2)

# [1.3.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.2.1...v1.3.0) (2025-08-02)


### Features

* 整合图片信息到view_image并修复get_image_info bug ([#1](https://github.com/donghao1393/mcp-imgutils/issues/1)) ([05908af](https://github.com/donghao1393/mcp-imgutils/commit/05908af0f7125057f4e95fa4ca514813a431be97))

# [1.2.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.1.1...v1.2.0) (2025-08-01)


### Features

* 采用Desktop Commander的图片处理方法 ([0cca373](https://github.com/donghao1393/mcp-imgutils/commit/0cca37377fe2c612497c4cfcb9d2706f34c9b377))

## [1.1.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.1.0...v1.1.1) (2025-08-01)


### Bug Fixes

* 修复代码风格问题 ([52f805f](https://github.com/donghao1393/mcp-imgutils/commit/52f805ff10a92ba6cf112b8e23590b6d65188946))

# [1.1.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.3...v1.1.0) (2025-08-01)


### Features

* 实现智能图片压缩以适应MCP响应大小限制 ([142061b](https://github.com/donghao1393/mcp-imgutils/commit/142061bc6cd69521e57a856ec9b1055fbdec1d1e))

## [1.0.3](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.2...v1.0.3) (2025-04-07)


### Bug Fixes

* 修复代码风格和集成测试问题 ([ac6775f](https://github.com/donghao1393/mcp-imgutils/commit/ac6775feac25fc9eed0d21d2405f7bf7cbb05cb1))

## [1.0.2](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.1...v1.0.2) (2025-04-07)


### Bug Fixes

* 修复代码风格和测试问题 ([c530ce9](https://github.com/donghao1393/mcp-imgutils/commit/c530ce9d5f9cb4229dca03689f16138bda774c69))

## [1.0.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.0...v1.0.1) (2025-04-07)


### Bug Fixes

* 修复CI/CD工作流问题 ([29f308b](https://github.com/donghao1393/mcp-imgutils/commit/29f308b99e9402cac7aeb6a58cb0ad46316c1d55))

# 1.0.0 (2025-04-07)


### Features

* 添加CI/CD配置和测试框架 ([d8b9576](https://github.com/donghao1393/mcp-imgutils/commit/d8b9576fb82a1ee98486b2e1e4011a02635ebcb2))
