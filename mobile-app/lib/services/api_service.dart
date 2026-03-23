import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  // TODO: Change to your actual backend URL when deploying
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // Store Firebase JWT token securely
  Future<void> saveToken(String token) async {
    await _storage.write(key: 'firebase_token', value: token);
  }

  // Get stored token
  Future<String?> getToken() async {
    return await _storage.read(key: 'firebase_token');
  }

  // Clear token on logout
  Future<void> clearToken() async {
    await _storage.delete(key: 'firebase_token');
  }

  // POST /api/v1/auth/login
  // Called once after Firebase Phone Auth succeeds
  // Returns user profile with role
  Future<Map<String, dynamic>?> loginWithFirebaseToken(String firebaseToken) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $firebaseToken',
        },
        body: jsonEncode({'fcm_token': ''}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Save token for future requests
        await saveToken(firebaseToken);
        debugPrint('Login successful: ${data['role']}');
        return data;
      } else {
        debugPrint('Login failed: ${response.statusCode} ${response.body}');
        return null;
      }
    } catch (e) {
      debugPrint('Login error: $e');
      return null;
    }
  }

  // GET /api/v1/auth/me
  // Get current user profile
  Future<Map<String, dynamic>?> getCurrentUser() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('Get current user error: $e');
      return null;
    }
  }
}