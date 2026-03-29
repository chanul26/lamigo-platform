import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'Features/Splash/Presentation/splash_screen.dart';
import 'Features/Auth/Presentation/login_screen.dart';
import 'Features/Home/Presentation/home_screen.dart';
import 'Features/Trip/Presentation/trip_screen.dart';
import 'Features/Trip/Presentation/stop_detail_screen.dart';
import 'Features/Trip/Presentation/emergency_screen.dart';
import 'Features/Home/Presentation/driver_profile_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/home': (context) => const HomeScreen(),
        '/profile': (context) => const DriverProfileScreen(),
        '/trip': (context) {
          final tripId =
              ModalRoute.of(context)!.settings.arguments as String? ?? '';
          return TripScreen(tripId: tripId);
        },
        '/stop-detail': (context) {
          final taskId =
              ModalRoute.of(context)!.settings.arguments as String? ?? '';
          return StopDetailScreen(stopId: taskId);
        },
        '/emergency': (context) {
          final tripId =
              ModalRoute.of(context)!.settings.arguments as String? ?? '';
          return EmergencyScreen(tripId: tripId);
        },
      },
    ),
  );
}
