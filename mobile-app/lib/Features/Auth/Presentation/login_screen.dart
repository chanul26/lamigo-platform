import 'package:flutter/material.dart';

import 'package:lamigo_mobile/core/constants/app_colors.dart';
import 'package:lamigo_mobile/core/constants/app_text_styles.dart';

/// Placeholder login screen – full UI to be implemented per Figma design.
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Center(
          child: Text(
            'Login',
            style: AppTextStyles.headline2,
          ),
        ),
      ),
    );
  }
}
