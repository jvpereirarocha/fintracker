# CHANGELOG

<!-- version list -->

## v1.4.0 (2026-11-09)

### Bug Fixes

- Keep SQL parameter values out of error logs
  ([`a369942`](https://github.com/jvpereirarocha/fintracker/commit/a369942d8615fcfa5ea762212d7a601191fab270))

### Features

- Log one JSON line per API request
  ([`40075fe`](https://github.com/jvpereirarocha/fintracker/commit/40075feb8d2450ee3761a566db7ff745422d69a9))


## v1.3.0 (2026-11-09)

### Bug Fixes

- **build**: Show pytest output when running make test in a terminal
  ([`af1396b`](https://github.com/jvpereirarocha/fintracker/commit/af1396b8303efb67b1788403ed2308b462af7ffd))

### Build System

- Add dockerized test environment and Makefile
  ([`ebbc4ff`](https://github.com/jvpereirarocha/fintracker/commit/ebbc4ff40535f7f321a62ea32d43b6f316e3be8a))

### Documentation

- Add OpenAPI spec including dashboard chart endpoints
  ([`55259df`](https://github.com/jvpereirarocha/fintracker/commit/55259dfd7a1c5a8ce2f444d1900db0965bcfab7f))

- Use a generic username in the OpenAPI example
  ([`b0c5e92`](https://github.com/jvpereirarocha/fintracker/commit/b0c5e92018a7849ad0add6f412b4f2b5de7d32a7))

### Features

- Add dashboard chart endpoints for monthly totals and expenses by category
  ([`ba653bc`](https://github.com/jvpereirarocha/fintracker/commit/ba653bc5efd3b9bf04f1319bab869cceb02bb4c0))


## v1.2.0 (2026-11-05)

### Features

- Add orderBy to transaction listing and break ties by id
  ([`3daf525`](https://github.com/jvpereirarocha/fintracker/commit/3daf525ef57279aa92a24b5164a86f106bbb40f1))


## v1.1.0 (2026-11-04)

### Bug Fixes

- Formatting files
  ([`6583c1d`](https://github.com/jvpereirarocha/fintracker/commit/6583c1d4bd6e69ee7023c8452e1bb1cda3af03cf))

- Scope expense unique index per user and return 409 on duplicates
  ([#2](https://github.com/jvpereirarocha/fintracker/pull/2),
  [`f950fb5`](https://github.com/jvpereirarocha/fintracker/commit/f950fb5be6a86e59162cd4fbde24d929d2922327))

### Documentation

- Add CLAUDE.md file in my project
  ([`0534138`](https://github.com/jvpereirarocha/fintracker/commit/0534138b7ce06b8d16330aa7e8ba3703989e6a9a))

### Features

- Implementing release versioning
  ([`2eee0d8`](https://github.com/jvpereirarocha/fintracker/commit/2eee0d84d35a422b583497eea158ac43de18506c))


## v1.0.0 (2026-04-26)

- Initial Release
