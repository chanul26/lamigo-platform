import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../core/constants.dart';

class ApiService {
  Future<bool> login(String driverId, String password) async {
    try {
      // We override the base URL just for the health check
      final response = await http.get(Uri.parse('http://10.0.2.2:8000/api/health'));
      if (response.statusCode == 200) {
        debugPrint('Backend Connected!');
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
