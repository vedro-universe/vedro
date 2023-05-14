# Changelog

## v1.8

### v1.8.3 (2022-12-04)

- Fix Orderer [#44](https://github.com/tsv1/vedro/pull/44)

### v1.8.2 (2022-11-27)

- Fix file loader [#4466e9f](https://github.com/tsv1/vedro/commit/4466e9f0b3bb036f836851fb22e754022fb8c795)
- Fix scenario init order [#239b05a](https://github.com/tsv1/vedro/commit/239b05a40847ce51306b991064cfd812f8db9bbb)

### v1.8.1 (2022-11-21)

- Fix Orderer plugin [#8ecb35f](https://github.com/tsv1/vedro/commit/8ecb35f44ae54ef343e38c21238ede24dcc91545)

### v1.8.0 (2022-11-20)

- [Core] Add graceful interruptions [#39](https://github.com/tsv1/vedro/pull/39)
- [Interrupter] Add `-f` argument [#39](https://github.com/tsv1/vedro/pull/39)
- [Skipper] Add `@skip_if` [#32](https://github.com/tsv1/vedro/pull/42)
- [Orderer] Add plugin [#37](https://github.com/tsv1/vedro/pull/37)
- [DryRunner] Add plugin [#36](https://github.com/tsv1/vedro/pull/36)
- [RichReporter] Add `--hide-namespaces` argument [#ad75e42](https://github.com/tsv1/vedro/commit/ad75e42a71d032669da61e14b4eccf3119261683)
- [PyCharm Reporter] Add `--pycharm-no-output` argument [#38](https://github.com/tsv1/vedro/pull/38)


## v1.7

### v1.7.0 (2022-09-04)

- [Core] Add `Registry` [#33](https://github.com/tsv1/vedro/pull/33)
- [Core] Add `ScenarioOrderer` [#34](https://github.com/tsv1/vedro/pull/34)
- [Core] Add `ScenarioScheduler` [#32](https://github.com/tsv1/vedro/pull/32)
- [Core] Add `ScenarioReportedEvent` [#32](https://github.com/tsv1/vedro/pull/32)
- [Core] Add `AggregatedResult` [#32](https://github.com/tsv1/vedro/pull/32)
- [Core] Change `VirtualScenario.unique_id` impl [#32](https://github.com/tsv1/vedro/pull/32)
- [Core] Fix `@context` typing [#32](https://github.com/tsv1/vedro/pull/32)
- [Core] Fix `Deferrer` and `Artifacted` order [#33](https://github.com/tsv1/vedro/pull/33)
- [Rich Reporter] Add `RichPrinter` [#32](https://github.com/tsv1/vedro/pull/32)
- [Rich Reporter] Add `show_skipped` param [#32](https://github.com/tsv1/vedro/pull/32)
- [PyCharm Reporter] Set `show_skipped=True` by default [#32](https://github.com/tsv1/vedro/pull/32)
- [Interrupter] Add `--ff` argument [#32](https://github.com/tsv1/vedro/pull/32)
- [Repeater] Add plugin [#32](https://github.com/tsv1/vedro/pull/32)


## v1.6

### v1.6.0 (2022-06-05)

- [Core] Add artifacts [#29](https://github.com/tsv1/vedro/pull/29), [#30](https://github.com/tsv1/vedro/pull/30)
- [Artifacted] Add plugin [#31](https://github.com/tsv1/vedro/pull/31)


## v1.5

### v1.5.1 (2022-05-20)

- [Core] Update dependencies [#daeed79](https://github.com/tsv1/vedro/commit/daeed79e61b475e63c9df74b92460246b83605e6)
- [Rich Reporter] Add `show_scenario_spinner` param [#72702d9](https://github.com/tsv1/vedro/commit/72702d9270cdac3c3efb1140a9e70e95d337b585)

### v1.5.0 (2022-04-24)

- [Core] Add plugin configuration [#27](https://github.com/tsv1/vedro/pull/27)
- [Core] Restrict scenario subclassing [#dd51c16](https://github.com/tsv1/vedro/commit/dd51c16400993d0fe1fd34bba57edff710ac2638)
- [Rich Reporter] Fix pluralizing in summary [#26](https://github.com/tsv1/vedro/pull/26)
- [Rich Reporter] Limit traceback [#25](https://github.com/tsv1/vedro/pull/25)
- [Rich Reporter] Add `--show-paths` param [#24](https://github.com/tsv1/vedro/pull/24)


## v1.4

### v1.4.0 (2022-01-09)

- [Core] Add `vedro run` command [#20](https://github.com/tsv1/vedro/pull/20)
- [Core] Move `vedro._core` to `vedro.core` [#21](https://github.com/tsv1/vedro/pull/21)


## v1.3

### v1.3.6 (2021-12-17)

- [PyCharm Reporter] Add `--pycharm-show-skipped` and `--pycharm-show-internal-calls` params [#205d914](https://github.com/tsv1/vedro/commit/205d9140caefc6d10781043cf78f42ab7c226966)

### v1.3.5 (2021-12-16)

- [PyCharm Reporter] Add PyCharm Reporter (for [IntelliJ IDEA Plugin](https://plugins.jetbrains.com/plugin/18227-vedro)) [#19](https://github.com/tsv1/vedro/pull/19)

### v1.3.4 (2021-12-16)

- [Skipper] Add support for selecting template scenarios [#18](https://github.com/tsv1/vedro/pull/18)

### v1.3.3 (2021-11-11)

- [Rich Reporter] Fix duplicated namespace [#c02a1de](https://github.com/tsv1/vedro/commit/c02a1de6a4626a39fb3653ff3f204dceec5430e9)
