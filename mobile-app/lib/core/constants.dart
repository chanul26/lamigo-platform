/// App-wide constants for the LamiGo Driver mobile app.
class AppConstants {
  AppConstants._(); // prevent instantiation

  /// API base URL for backend requests.
  /// Use 10.0.2.2 on Android emulator to reach the host machine's localhost.
  static const String apiBaseUrl = 'http://10.0.2.2:8000/api/v1';
}
