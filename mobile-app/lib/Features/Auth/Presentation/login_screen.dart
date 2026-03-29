import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Controllers for real input
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    setState(() => _isLoading = true);
    try {
      // REPLACE /api/health with real Firebase Sign-in
      UserCredential userCredential = await _auth.signInWithEmailAndPassword(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );

      String? token = await userCredential.user?.getIdToken();

      if (token != null) {
        // REQUIREMENT: Use flutter_secure_storage, NOT SharedPreferences
        await _storage.write(key: 'auth_token', value: token);

        if (mounted) {
          Navigator.pushReplacementNamed(context, '/home');
        }
      }
    } on FirebaseAuthException catch (e) {
      // REQUIREMENT: Show Firebase error code
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.code}')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

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
            const Text("Driver Login", textAlign: TextAlign.center, 
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            TextField(
              controller: _emailController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(hintText: "Email", filled: true, 
                  fillColor: const Color(0xFF1E1E1E), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(hintText: "Password", filled: true, 
                  fillColor: const Color(0xFF1E1E1E), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _isLoading ? const CircularProgressIndicator() : const Text("LOGIN"),
            ),
          ],
        ),
      ),
    );
  }
}