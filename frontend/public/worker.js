self.addEventListener('push', function(event) {
    const data = event.data.json();
    console.log('Push Received:', data);
  
    const title = 'New Message';
    const options = {
      body: data.message,
      icon: '/icon.png'  // Add your notification icon here
    };
  
    event.waitUntil(self.registration.showNotification(title, options));
  });





