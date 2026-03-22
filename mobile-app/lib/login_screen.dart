import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; 

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  //Added Controllers to capture real input
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  
  //Initialize Secure Storage 
  final _storage = const FlutterSecureStorage();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) return;

    setState(() => _isLoading = true);

    try {
      // Real Firebase Sign-In (Replaces /api/health)
      UserCredential userCredential = await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );

      // FIX: Get JWT Token
      String? token = await userCredential.user?.getIdToken();

      if (token != null) {
        // FIX: Store in Secure Storage
        await _storage.write(key: 'jwt_token', value: token);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Login Successful')),
          );
          Navigator.pushReplacementNamed(context, '/home');
        }
      }
    } on FirebaseAuthException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: ${e.message}"), backgroundColor: Colors.red),
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
            const Icon(Icons.lock_person, size: 80, color: Colors.blueAccent),
            const SizedBox(height: 40),
            const Text("Driver Login", textAlign: TextAlign.center, 
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            
            // Email Field
            TextField(
              controller: _emailController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Email", 
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true, 
                fillColor: const Color(0xFF1E1E1E), 
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))
              ),
            ),
            const SizedBox(height: 16),
            
            // Password Field
            TextField(
              controller: _passwordController,
              obscureText: true,
              style: const TextStyle(color: TextStyle(color: Colors.white).color),
              decoration: InputDecoration(
                hintText: "Password", 
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true, 
                fillColor: const Color(0xFF1E1E1E), 
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))
              ),
            ),
            const SizedBox(height: 24),
            
            ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent, 
                padding: const EdgeInsets.symmetric(vertical: 16)
              ),
              child: _isLoading 
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white))
                : const Text("LOGIN"),
            ),
          ],
        ),
      ),
    );
  }
}