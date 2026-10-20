---
name: Fluxo Flutter e Dart
description: Use em projetos Flutter/Dart — estrutura do app, estado, testes, análise estática, build e integração com APIs
---

## Antes de mexer

Leia `pubspec.yaml` (dependências, SDK constraints), `analysis_options.yaml`, estrutura `lib/` e `AGENTS.md` local. Confirme o ambiente:

```bash
flutter --version      # versão do SDK
flutter pub deps       # árvore de dependências
```

## Comandos de validação (rode sempre)

```bash
flutter analyze        # lint/estática — deve ficar sem erros
flutter test           # testes unitários e de widget
dart format .          # formatação
flutter pub get         # após mexer no pubspec
```

## Padrões

- Estrutura por **recurso** (`lib/features/login/...`) ou camadas claras (`data/domain/presentation`) — siga a existente.
- Estado: Riverpod/Bloc/Provider **já usado no projeto**; não introduza framework novo sem pedido.
- Assíncrono: `async/await` com tratamento de erro visível ao usuário; nunca `catch (_) {}` silencioso.
- Separe regra de negócio (Dart puro, testável) da UI (widgets finos).
- Widgets devem ser `const` quando possível; evite rebuild desnecessário.

## Integração

- Cliente HTTP isolado (ex.: `http`/`dio`) com timeout, base URL por ambiente e erros tipados.
- Segredos **nunca** no código — use `--dart-define` ou arquivo `.env` fora do versionamento.

## Testes

- `test/` para lógica pura; `test/widget_test.dart` para UI; `integration_test/` para fluxo completo.
- Alvo de build rápido para verificação: `flutter run -d linux` ou `flutter build apk --debug`.

## Checklist de saída

`flutter analyze` limpo → `flutter test` passando → resumo do que mudou e como validar.
