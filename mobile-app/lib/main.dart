import 'package:flutter/material.dart';

import 'package:lamigo_mobile/core/constants/app_colors.dart';
import 'package:lamigo_mobile/features/auth/presentation/login_screen.dart';
import 'package:lamigo_mobile/features/splash/presentation/splash_screen.dart';

void main() {
  runApp(const LamiGoApp());
}

class LamiGoApp extends StatelessWidget {
  const LamiGoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LamiGo',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.light(
          primary: AppColors.brandOrange,
          surface: AppColors.background,
          onSurface: AppColors.onSurface,
        ),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
      },
    );
  }
}
