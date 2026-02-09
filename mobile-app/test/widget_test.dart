import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:lamigo_mobile/main.dart';

void main() {
  testWidgets('App starts with splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const LamiGoApp());

    // Splash screen shows: either logo image or placeholder icon
    expect(find.byType(Scaffold), findsOneWidget);
  });
}
