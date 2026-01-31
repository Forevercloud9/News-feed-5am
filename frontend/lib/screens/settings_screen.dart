import 'package:flutter/material.dart';
import '../services/firestore_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // 1. Genre Selection State
  final Map<String, bool> _genreSettings = {
    'Domestic Business (Japan)': true,
    'Global Business': true,
    'Finance & Markets': true,
    'Global Tech & Startups': false,
    'New Technologies': false,
    'Corporate Tracking (JT/BAT)': false,
    'Entertainment & Music Fests': false,
  };

  // 2. Email Management State
  final List<Map<String, dynamic>> _emailRecipients = [
    {'email': 'user@example.com', 'isActive': true},
  ];

  final TextEditingController _emailController = TextEditingController();
  final FirestoreService _firestoreService = FirestoreService();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final data = await _firestoreService.loadSettings();
    if (data != null) {
      setState(() {
        // Update Genres
        if (data['preferences'] != null) {
          final loadedGenres = data['preferences'] as Map<String, bool>;
          // Merge to keep keys safe
          _genreSettings.forEach((key, val) {
            if (loadedGenres.containsKey(key)) {
              _genreSettings[key] = loadedGenres[key]!;
            }
          });
        }
        
        // Update Emails
        if (data['email_recipients'] != null) {
          final loadedEmails = data['email_recipients'] as List<String>;
          _emailRecipients.clear();
          for (var email in loadedEmails) {
            _emailRecipients.add({'email': email, 'isActive': true});
          }
        }
      });
    }
    setState(() => _isLoading = false);
  }

  Future<void> _saveData() async {
    setState(() => _isLoading = true);
    
    // Extract active emails only? Or all? Let's save all active ones for now.
    // The UI supports isActive, but backend simple list doesn't map 1:1 perfectly unless we change schema.
    // For MVP, let's just save the emails that are in the list (ignoring isActive flag implementation detail for backend simplicity 
    // OR filter active ones. Let's filter active ones).
    
    final activeEmails = _emailRecipients
        .where((e) => e['isActive'] == true)
        .map((e) => e['email'] as String)
        .toList();

    try {
      await _firestoreService.saveSettings(
        genres: _genreSettings,
        emails: activeEmails,
      );
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Settings saved successfully!')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving settings: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  void _addEmail() {
    if (_emailController.text.isNotEmpty && _emailController.text.contains('@')) {
      setState(() {
        _emailRecipients.add({
          'email': _emailController.text,
          'isActive': true,
        });
        _emailController.clear();
      });
    }
  }

  void _removeEmail(int index) {
    setState(() {
      _emailRecipients.removeAt(index);
    });
  }

  void _toggleEmailActive(int index, bool? value) {
    setState(() {
      _emailRecipients[index]['isActive'] = value ?? false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          if (_isLoading)
            const Center(child: Padding(
              padding: EdgeInsets.only(right: 16.0),
              child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
            ))
          else
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _saveData,
              tooltip: 'Save Settings',
            ),
        ],
      ),
      body: ListView(
        children: [
          // Section 1: Genre Selection
          _buildSectionHeader('News Genres'),
          ..._genreSettings.keys.map((key) {
            return CheckboxListTile(
              title: Text(key),
              value: _genreSettings[key],
              onChanged: (bool? value) {
                setState(() {
                  _genreSettings[key] = value ?? false;
                });
              },
            );
          }),

          const Divider(height: 32),

          // Section 2: Email Delivery Settings
          _buildSectionHeader('Email Delivery Settings'),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: 'Add Recipient Email',
                      hintText: 'name@example.com',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    keyboardType: TextInputType.emailAddress,
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  onPressed: _addEmail,
                  icon: const Icon(Icons.add),
                  label: const Text('Add'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          
          if (_emailRecipients.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text('No recipients added yet.', style: TextStyle(color: Colors.grey)),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _emailRecipients.length,
              itemBuilder: (context, index) {
                final recipient = _emailRecipients[index];
                return ListTile(
                  leading: Checkbox(
                    value: recipient['isActive'],
                    onChanged: (val) => _toggleEmailActive(index, val),
                  ),
                  title: Text(recipient['email']),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    onPressed: () => _removeEmail(index),
                  ),
                );
              },
            ),
          
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.primary,
            ),
      ),
    );
  }
}
