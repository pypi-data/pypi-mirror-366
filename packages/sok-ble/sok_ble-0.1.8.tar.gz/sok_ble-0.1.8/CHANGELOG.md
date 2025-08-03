# CHANGELOG


## [0.1.8](https://github.com/IAmTheMitchell/sok-ble/compare/v0.1.7...v0.1.8) (2025-08-03)


### Bug Fixes

* fix release ([9257795](https://github.com/IAmTheMitchell/sok-ble/commit/9257795edaa5937371fd3870ae7434a468bbdca2))
* fix release ([25395a2](https://github.com/IAmTheMitchell/sok-ble/commit/25395a22d35d62516b5ddb5d1be5e944e654cf15))

## [0.1.7](https://github.com/IAmTheMitchell/sok-ble/compare/v0.1.6...v0.1.7) (2025-08-03)


### Bug Fixes

* fix bleak import ([e413bb7](https://github.com/IAmTheMitchell/sok-ble/commit/e413bb75ad3e10a73dba08881829e76dc8358d2c))


### Documentation

* update CI badges ([a3f4f24](https://github.com/IAmTheMitchell/sok-ble/commit/a3f4f2478dc96a8861820adce5b40eeab1bb581d))

## v0.1.6 (2025-07-13)

### Bug Fixes

- Prevent reconnect loop in async context
  ([`688d298`](https://github.com/IAmTheMitchell/sok-ble/commit/688d29874cb09c2ea40df818d07122d1bad32141))


## v0.1.5 (2025-07-13)

### Bug Fixes

- Resolve ruff line length issues
  ([`70805c0`](https://github.com/IAmTheMitchell/sok-ble/commit/70805c0b211ca3691099709eb73af0f3fba6d530))

### Build System

- Build with hatchling
  ([`935093e`](https://github.com/IAmTheMitchell/sok-ble/commit/935093e7ade6125311ec7492d2f535645226d8fd))

- Fix uv.lock and add ruff
  ([`00cce38`](https://github.com/IAmTheMitchell/sok-ble/commit/00cce388be9ccc88a9a33d8f7660a03928bcd963))

### Chores

- Add background and additional guidance
  ([`6e3ad00`](https://github.com/IAmTheMitchell/sok-ble/commit/6e3ad00adce528a852acbd098a757c8e813cf0b0))

### Continuous Integration

- Add ruff
  ([`1a7ad6d`](https://github.com/IAmTheMitchell/sok-ble/commit/1a7ad6d45d4d5e24ffe59b9098f4e9dfab4bfa8a))

### Refactoring

- Fix ruff linting errors
  ([`859624d`](https://github.com/IAmTheMitchell/sok-ble/commit/859624d5bc3c4a556f24edb34bdad14f5e991333))


## v0.1.4 (2025-06-10)

### Bug Fixes

- Downgrade async-timeout
  ([`ce2e655`](https://github.com/IAmTheMitchell/sok-ble/commit/ce2e6557da8e1dcefe9c2a6b2817e9adf56d4423))


## v0.1.3 (2025-06-10)

### Bug Fixes

- Handle GATT race on connect
  ([`a9feacc`](https://github.com/IAmTheMitchell/sok-ble/commit/a9feaccb1f3d9a06128eb7f3b301b9ef292de94a))

### Refactoring

- Use services property
  ([`f847a68`](https://github.com/IAmTheMitchell/sok-ble/commit/f847a689ec794a0034b0e367dd1fc43057938e42))


## v0.1.2 (2025-06-09)

### Bug Fixes

- Allow older bleak-retry-connector version
  ([`9b7a343`](https://github.com/IAmTheMitchell/sok-ble/commit/9b7a34356282885bcc0c14da42e3fe142c6347f6))

### Chores

- Remove duplicate files
  ([`8862838`](https://github.com/IAmTheMitchell/sok-ble/commit/8862838245b4096bff1c8506da67e1e676ebdcc5))

### Documentation

- Add references
  ([`23f7e8f`](https://github.com/IAmTheMitchell/sok-ble/commit/23f7e8fbd367115d6ac9890feafa249014a14488))

### Refactoring

- Move into src folder
  ([`22f5ecf`](https://github.com/IAmTheMitchell/sok-ble/commit/22f5ecf3b0f6b2ae30b8b2a0d140360027d45ed1))

- Remove main.py
  ([`9c64246`](https://github.com/IAmTheMitchell/sok-ble/commit/9c64246565b74bf0a000263ed58ed8f9dde42e13))


## v0.1.1 (2025-06-08)

### Bug Fixes

- Correct parsing and notification flow
  ([`4332a40`](https://github.com/IAmTheMitchell/sok-ble/commit/4332a401f9c91727bbd7f9fbdde1fc4e3fe96863))

- Correct temperature parsing
  ([`f99e5c3`](https://github.com/IAmTheMitchell/sok-ble/commit/f99e5c3d8f39b6a84ae5f42083d6e21ad6d4dbdc))

- Use BLE notifications for commands
  ([`a99d02b`](https://github.com/IAmTheMitchell/sok-ble/commit/a99d02b3f37221e8becf893ba570c6cd8eadfbd7))

### Testing

- Add integration mock test
  ([`6b2971c`](https://github.com/IAmTheMitchell/sok-ble/commit/6b2971cb9b078a4289681a0f180fc3ef248d5828))


## v0.1.0 (2025-06-06)

### Build System

- Add bleak and pytest dependencies
  ([`8d95239`](https://github.com/IAmTheMitchell/sok-ble/commit/8d9523999267eb60ed745a4c7311869cf7e10e66))

- Enable build CI/CD steps
  ([`e8c0256`](https://github.com/IAmTheMitchell/sok-ble/commit/e8c0256f427410f246a6849fff1c1e13c81e07bc))

- Update build system
  ([`cf60106`](https://github.com/IAmTheMitchell/sok-ble/commit/cf60106b73c495e7346268d1dfb54ea209c89786))

- Update CI and pyproject.toml
  ([`bd75ab7`](https://github.com/IAmTheMitchell/sok-ble/commit/bd75ab77cbd009cd6bcf8f6598e85129161fb91e))

### Chores

- Add funding
  ([`336244f`](https://github.com/IAmTheMitchell/sok-ble/commit/336244f7abdb0d37d3d841034cf18ef411f81b89))

- Add license
  ([`8394fef`](https://github.com/IAmTheMitchell/sok-ble/commit/8394fef0f82cd26608407b77d327e051c8a00909))

- Add LLM instruction files
  ([`8a6c21e`](https://github.com/IAmTheMitchell/sok-ble/commit/8a6c21e22f707ab710bd8055c4591ea639059089))

- Add more comprehensive gitignore
  ([`b814c79`](https://github.com/IAmTheMitchell/sok-ble/commit/b814c79600104776b36f556eb1be55b5c79067ed))

- Instruct agents to use conventional commits
  ([`7e194c7`](https://github.com/IAmTheMitchell/sok-ble/commit/7e194c77d6ecfc3676c52e60526d8b8701bb5323))

### Features

- Add debug logging and update docs
  ([`3a60baa`](https://github.com/IAmTheMitchell/sok-ble/commit/3a60baa27fea9b5ce89b924ece0926f55f2ff9d7))

- Compute derived metrics
  ([`f33e71d`](https://github.com/IAmTheMitchell/sok-ble/commit/f33e71da4214a6bebe3b0ca5e5c086fb87b5842e))

- Implement full polling update
  ([`3828ff2`](https://github.com/IAmTheMitchell/sok-ble/commit/3828ff2f73ef658c8fd1762ef87c10e0a842d85e))

- Initial commit
  ([`6181aee`](https://github.com/IAmTheMitchell/sok-ble/commit/6181aee704f821df9d4ed15bd7b68d24ee13c67c))
