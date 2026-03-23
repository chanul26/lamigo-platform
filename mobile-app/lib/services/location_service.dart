import 'dart:async';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:geolocator/geolocator.dart';

class LocationService {
  Timer? _timer;
  final FirebaseDatabase _db = FirebaseDatabase.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  void startTracking() {
    // Member B Requirement: 15s interval
    _timer = Timer.periodic(const Duration(seconds: 15), (timer) async {
      await _updateLocation();
    });
  }

  Future<void> _updateLocation() async {
    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      String? driverId = _auth.currentUser?.uid;
      if (driverId != null) {
        // Update Firebase Realtime Database
        await _db.ref('driver_locations/$driverId').set({
          'lat': position.latitude,
          'lng': position.longitude,
          'updated_at': ServerValue.timestamp,
        });
      }
    } catch (e) {
      print("Location Error: $e");
    }
  }

  void stopTracking() {
    _timer?.cancel();
  }
}