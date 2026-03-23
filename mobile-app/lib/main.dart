import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'Features/Splash/Presentation/splash_screen.dart';
import 'Features/Auth/Presentation/login_screen.dart';
import 'Features/Home/Presentation/home_screen.dart';
import 'Features/Trip/Presentation/trip_screen.dart';
<<<<<<< HEAD
import 'Features/Trip/Presentation/stop_detail_screen.dart';
=======
>>>>>>> 22bfb77afff900807015d468edb7dcd53f61b0f4

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/trip',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/home': (context) => const HomeScreen(),
        '/trip': (context) => const TripScreen(tripId: 'TRP-001'),
<<<<<<< HEAD
        '/stop-detail': (context) =>  StopDetailScreen(stopId: 'STOP-001'),

=======
>>>>>>> 22bfb77afff900807015d468edb7dcd53f61b0f4
      },
    ),
  );
}