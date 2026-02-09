import 'package:flutter/material.dart';

/// LamiGo design system colors from Figma.
/// Primary brand: LamiGo Orange. Theme: modern, clean, professional.
class AppColors {
  AppColors._();

  // ----- Brand -----
  /// LamiGo Orange – primary brand color
  static const Color brandOrange = Color(0xFFFA7D43);

  // ----- Backgrounds -----
  /// Main app background (Figma: Background)
  static const Color background = Color(0xFFF4F7F9);
  /// Soft white for cards/surfaces (Figma: Soft-White)
  static const Color softWhite = Color(0xFFF3F4F6);

  // ----- Text / On-surface -----
  /// Primary text, icons, buttons (Figma: Text-Primary, Charcoal, On Surface)
  static const Color textPrimary = Color(0xFF1F2937);
  static const Color onSurface = Color(0xFF1D1B20);
  /// Secondary text, placeholders (Figma: Text-Secondary)
  static const Color textSecondary = Color(0xFF6B7280);

  // ----- UI state -----
  /// Primary blue tint (e.g. selected state)
  static const Color primaryBlue200 = Color(0xFFDDE7FB);
  static const Color warning400 = Color(0xFFF6B951);
  static const Color success500 = Color(0xFF16A34A);
  static const Color error500 = Color(0xFFDC2626);

  // ----- Common -----
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);
}
