// lib/Features/Home/Presentation/home_screen.dart
import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("LamiGo Driver")),
      body: Center(
        child: ElevatedButton(
          onPressed: () => Navigator.pushNamed(context, '/trip'),
          child: const Text("View Active Trip"),
        ),
      ),
    );
  }
}