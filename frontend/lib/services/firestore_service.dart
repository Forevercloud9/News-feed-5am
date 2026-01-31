import 'package:cloud_firestore/cloud_firestore.dart';

class FirestoreService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;
  // For MVP, we use a fixed user ID since we don't have Auth implemented yet.
  final String _userId = 'default_user'; 

  /// Saves the current settings to Firestore
  Future<void> saveSettings({
    required Map<String, bool> genres,
    required List<String> emails,
  }) async {
    try {
      await _db.collection('users').doc(_userId).set({
        'preferences': genres,
        'email_recipients': emails,
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      print('Error saving settings: $e');
      rethrow;
    }
  }

  /// Loads settings from Firestore
  /// Returns a Map with 'genres' and 'emails', or null if error/empty.
  Future<Map<String, dynamic>?> loadSettings() async {
    try {
      final doc = await _db.collection('users').doc(_userId).get();
      if (doc.exists && doc.data() != null) {
        final data = doc.data()!;
        return {
          'preferences': Map<String, bool>.from(data['preferences'] ?? {}),
          'email_recipients': List<String>.from(data['email_recipients'] ?? []),
        };
      }
    } catch (e) {
      print('Error loading settings: $e');
    }
    return null;
  }
}
