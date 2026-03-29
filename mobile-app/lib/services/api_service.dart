import 'dart:async';
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
  Future<Map<String, dynamic>?> loginWithFirebaseToken(
    String firebaseToken,
  ) async {
    debugPrint('[API] loginWithFirebaseToken: calling $baseUrl/auth/login');
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/auth/login'),
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $firebaseToken',
            },
            body: jsonEncode({'fcm_token': ''}),
          )
          .timeout(const Duration(seconds: 15));

      debugPrint('[API] Response status: ${response.statusCode}');
      debugPrint('[API] Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        await saveToken(firebaseToken);
        debugPrint(
          '[API] Login successful. role=${data['role']}, keys=${data.keys.toList()}',
        );
        return data;
      } else {
        debugPrint(
          '[API] Login failed: ${response.statusCode} ${response.body}',
        );
        return null;
      }
    } on TimeoutException {
      debugPrint(
        '[API] Request timed out after 15s — backend unreachable at $baseUrl',
      );
      rethrow;
    } catch (e, stack) {
      debugPrint('[API] Login exception: $e\n$stack');
      rethrow;
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
        headers: {'Authorization': 'Bearer $token'},
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

  // GET /api/v1/trips/
  Future<List<dynamic>?> getActiveTrips() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl/trips/?status=active'),
        headers: {'Authorization': 'Bearer $token'},
      );

      debugPrint(
        '[API] getActiveTrips: ${response.statusCode} ${response.body}',
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('getActiveTrips error: $e');
      return null;
    }
  }

  // GET /api/v1/tasks/
  Future<List<dynamic>?> getTasks(String tripId) async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl/tasks/?trip_id=$tripId'),
        headers: {'Authorization': 'Bearer $token'},
      );

      debugPrint('[API] getTasks: ${response.statusCode} ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('getTasks error: $e');
      return null;
    }
  }

  // GET /api/v1/tasks/{task_id}
  Future<Map<String, dynamic>?> getTask(String taskId) async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl/tasks/$taskId'),
        headers: {'Authorization': 'Bearer $token'},
      );

      debugPrint('[API] getTask: ${response.statusCode} ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('getTask error: $e');
      return null;
    }
  }

  // PATCH /api/v1/tasks/{task_id}
  Future<Map<String, dynamic>?> updateTask(
    String taskId,
    String status, {
    String? failureReason,
    String? driverNotes,
  }) async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final body = {
        'status': status,
        if (failureReason != null) 'failure_reason': failureReason,
        if (driverNotes != null && driverNotes.isNotEmpty)
          'driver_notes': driverNotes,
        'actual_arrival_time': DateTime.now().toIso8601String(),
      };

      final response = await http.patch(
        Uri.parse('$baseUrl/tasks/$taskId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(body),
      );

      debugPrint('[API] updateTask: ${response.statusCode} ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('updateTask error: $e');
      return null;
    }
  }

  // POST /api/v1/incidents/
  Future<Map<String, dynamic>?> createIncident(
    String tripId,
    String type,
    String description,
    double lat,
    double lng,
  ) async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.post(
        Uri.parse('$baseUrl/incidents/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'trip_id': tripId,
          'type': type,
          'description': description,
          'reported_at_lat': lat,
          'reported_at_lng': lng,
        }),
      );

      debugPrint(
        '[API] createIncident: ${response.statusCode} ${response.body}',
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('createIncident error: $e');
      return null;
    }
  }
}
