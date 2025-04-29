document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    load_mailbox('inbox')
    get_mail('inbox')
  });
  document.querySelector('#sent').addEventListener('click', () => {
    load_mailbox('sent')
    get_mail('sent')
  });
  document.querySelector('#archived').addEventListener('click', () => {
    load_mailbox('archive');
    get_mail('archive');
  });
  document.querySelector('#compose').addEventListener('click', () => {
    compose_email()
  });


  // Send Mail
  const form = document.getElementById('compose-form')
  form.addEventListener("submit", function(event) {
    event.preventDefault();
    const recipientsInput = document.getElementById('compose-recipients');
    const subjectInput = document.getElementById('compose-subject');
    const bodyInput = document.getElementById('compose-body');
    send_mail(recipientsInput.value, subjectInput.value, bodyInput.value);
  })


  document.querySelector('#reply-button').addEventListener("click", function() {
    const email_id = document.querySelector('.email-hidden').innerText;
    
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      const recipients = email.sender
      let subject = email.subject
      if (!subject.startsWith('Re:')) {
        subject = `Re: ${subject}`
      }
      const body = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`
      compose_email(recipients, subject, body)
    })
    compose_email(recipients, subject, body)
  })

  // By default, load the inbox
  load_mailbox('inbox');
  get_mail('inbox');
});

function compose_email(recipients='', subject='', body='') {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = recipients;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

}

function send_mail(recipients, subject, body) {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    load_mailbox('sent');
  })
  .catch(error => {
    console.error('Error during fetch', error);
  });
}

function get_mail(type) {
  fetch (`/emails/${type}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const email_div = document.createElement('div');
      const archive_button = document.createElement('input');
      archive_button.id = `archive-${email.id}`
      archive_button.className = 'archive-button';
      archive_button.type = 'submit';
      if (type === 'archive') {
        archive_button.value = 'Unarchive';
      } else {
        archive_button.value = 'Archive';
      }
      email_div.className = 'email-entry';
      email_div.id = `${email.id}`
      email_div.innerHTML = `
        <strong>${email.sender}</strong>  <strong class="email-subject">${email.subject}</strong> - ${email.body.slice(0, 50)}
        <span class="email-right" style="float: right;">${email.timestamp}</span>
      `;
      if (type === 'archive' || type === 'inbox') {
        email_div.querySelector('.email-right').appendChild(archive_button);
      }
      document.querySelector('#emails-view').appendChild(email_div);
    })

    show_email();
    if (type === 'archive' || type === 'inbox') {
      archive_load(type);
    }
  })
}

function view_email(email_id) {
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    const emailSubject = document.getElementById('email-subject');
    const emailSender = document.getElementById('email-sender');
    const emailBody = document.getElementById('email-body');
    const emailHidden = document.querySelector('.email-hidden');
    emailSubject.innerHTML = `
    <strong>Subject: ${email.subject}</strong>
    `;
    emailSender.innerHTML = `
    <strong>From: ${email.sender}</strong><span style="float: right;">${email.timestamp}</span>
    <p style="font-size: 15px;">To: ${email.recipients}</p>
    `;
    emailBody.innerHTML = `
    ${email.body}
    `;
    emailHidden.innerHTML = `${email_id}`
  })
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
} 

function show_email() {
  document.querySelectorAll('.email-entry').forEach(email_div => {
    email_div.addEventListener("click", function() {
      const email_id = this.id;
      view_email(email_id);
    })
  })
}



function archive_email(email_id, type) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: (type !== 'archive') 
    })
  })
  .then(() => {
    load_mailbox('inbox');
    get_mail('inbox');
  })
}

function archive_load(type) {
  document.querySelectorAll('.archive-button').forEach(archive_button => {
    archive_button.addEventListener("click", function(event) {
      event.stopPropagation();

      const email_id = this.closest('.email-entry').id;
      archive_email(email_id, type)

    })
  })
}
