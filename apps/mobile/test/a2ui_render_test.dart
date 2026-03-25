import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sanctum_mobile/main.dart';

void main() {
  testWidgets('Mobile Canvas placeholder test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the mobile canvas displays the expected placeholder text.
    expect(find.text('Mobile Canvas Ready.'), findsOneWidget);
    expect(find.text('Edge SLM Active (Privacy-First)'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
