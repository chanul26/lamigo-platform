import 'package:flutter/material.dart';
import 'Features/Splash/Presentation/splash_screen.dart';
import 'Features/Auth/Presentation/login_screen.dart';
import 'Features/Home/Presentation/home_screen.dart';

void main() => runApp(
      MaterialApp(
        debugShowCheckedModeBanner: false,
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/login': (context) => const LoginScreen(),
          '/home': (context) => const HomeScreen(),
        },
      ),
    );