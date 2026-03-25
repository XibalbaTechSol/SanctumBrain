# Sanctum Brain: Mobile Client (The Nomad Interface)

A Flutter-based mobile application that serves as the portable gateway to your Sanctum VPS.

## Core Features

- **Nomad Pulse**: Real-time WebSocket connection to the VPS for low-latency voice and UI state synchronization.
- **Mobile A2UI**: A subset of the A2UI framework optimized for mobile touch inputs and small form factors.
- **gRPC SecureChannel**: High-performance binary transport for streaming audio and multi-modal data.
- **Local NPU Offloading**: Utilizing on-device NPUs for rapid intent pre-classification.

## Structure

- `lib/components/`: Flutter-native A2UI atoms (e.g., `para_view.dart`).
- `lib/services/`: gRPC and WebSocket service clients.
- `lib/proto/`: Generated Dart code from `a2a.proto`.

## Getting Started

Ensure you have the Flutter SDK installed and a running Sanctum VPS:

```bash
flutter pub get
flutter run
```

## Protocol Buffers

Update gRPC definitions by re-generating the Dart code:

```bash
# From root
./ops/generate_proto.sh mobile
```
