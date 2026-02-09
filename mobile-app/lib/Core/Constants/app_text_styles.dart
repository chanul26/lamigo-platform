import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:lamigo_mobile/core/constants/app_colors.dart';

/// LamiGo text styles from Figma (Roboto via Google Fonts).
class AppTextStyles {
  AppTextStyles._();

  // ----- Headlines -----
  /// Headline 1 – Bold 32
  static TextStyle get headline1 => GoogleFonts.roboto(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        height: 1.0,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  /// Headline 2 – SemiBold 24
  static TextStyle get headline2 => GoogleFonts.roboto(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        height: 1.0,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  /// Headline 3 – SemiBold 20
  static TextStyle get headline3 => GoogleFonts.roboto(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        height: 1.0,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  // ----- Title -----
  /// Title Large – Medium 22, line height 28
  static TextStyle get titleLarge => GoogleFonts.roboto(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        height: 28 / 22,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  /// Title Medium – Medium 16, line height 24
  static TextStyle get titleMedium => GoogleFonts.roboto(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 24 / 16,
        letterSpacing: 0.15,
        color: AppColors.textPrimary,
      );

  // ----- Body -----
  /// Body Large – Regular 16
  static TextStyle get bodyLarge => GoogleFonts.roboto(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        height: 1.0,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  /// Body Small – Regular 12, line height 16
  static TextStyle get bodySmall => GoogleFonts.roboto(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 16 / 12,
        letterSpacing: 0.4,
        color: AppColors.textPrimary,
      );

  // ----- Labels / Buttons -----
  /// Button label – medium, primary
  static TextStyle get button => GoogleFonts.roboto(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.0,
        letterSpacing: 0,
        color: AppColors.white,
      );

  /// Caption / placeholder
  static TextStyle get caption => GoogleFonts.roboto(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: AppColors.textSecondary,
      );
}
