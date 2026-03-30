import 'package:flutter/material.dart';

import 'services/api_service.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.person_pin, size: 80, color: Colors.blueAccent),
            const SizedBox(height: 40),
            const Text("Driver Login", textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            TextField(
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(hintText: "Driver ID", filled: true, fillColor: const Color(0xFF1E1E1E), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () async {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Connecting to backend...')),
                );
                // TODO: Replace with real Firebase token + flow.
                await ApiService().loginWithFirebaseToken('dummy');
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(vertical: 16)),
              child: const Text("LOGIN"),
            ),
          ],
        ),
      ),
    );
  }
}