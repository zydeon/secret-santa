from email.message import EmailMessage
import random
import re
import smtplib, ssl
import sys
import time

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def is_valid_email(email):
  regex = r'[a-zA-Z_0-9][a-zA-Z_0-9\.]+[a-zA-Z_0-9]@[a-zA-Z_0-9]+\.[a-zA-Z_0-9\.]+[a-zA-Z_0-9]{2}'
  return re.fullmatch(regex, email)

def parse_credentials(f):
  with open(f) as fd:
    credentials = [l.strip() for l in fd.readlines()]

  # Check e-mail
  if not is_valid_email(credentials[0]):
    eprint('Sender\'s e-mail is invalid!')
    sys.exit(-1)

  # Check password
  if credentials[1] == '':
    eprint('Gave an empty password!')
    sys.exit(-1)

  return credentials

def parse_santas(f):
  santas = []
  with open(f) as f:
    try:
      santas = [{'name': s[0], 'email': s[1]} for s in [l.strip().split(',') for l in f.readlines()]]
    except:
      eprint("List of santas is not properly formatted, please check!")
      sys.exit(-1)

  # Check e-mail addresses.
  for s in santas:
    if not is_valid_email(s['email']):
      eprint(f'\'{s["name"]}\'s e-mail is invalid!')
      sys.exit(-1)

  # Check that no santa is duplicated (names or e-mails).
  if len(set([s['name'] for s in santas])) + len(set([s['email'] for s in santas])) != 2 * len(santas):
    eprint('Some names or e-mail addresses are duplicated!')
    sys.exit(-1)
  return santas

def confirm_santas(santas):
  print('Let\'s check that everyone\'s names and emails are correct one more time:\n')

  for i, s in enumerate(santas):
    print(f'{i+1}:\t{s["name"]}\t{s["email"]}')
  print()
  answer = input('Continue? (Yes: <ENTER>, No:<Ctrl-C>)')
  if answer == '':
    return True
  return False

def send_emails(santas, sender, password):
  SERVER = 'smtp.gmail.com'
  PORT = 587
  TIMEOUT_SECONDS = 10 
  MAX_ATTEMPTS = 10
  SUBJECT = 'Amigo secreto Natal 2020 :)'
  BODY = 'Olá {santa}!\n\nO teu amigo secreto é: {receiver}. SHHHHH!\n\nO limite são 15€.\n\nHo Ho Ho!'

  print(f'Connecting to SMTP server \'{SERVER}:{PORT}\'...')
  i = 0
  while i < MAX_ATTEMPTS:
    try:
      with smtplib.SMTP(SERVER, port=PORT, timeout=TIMEOUT_SECONDS) as smtp:
        print('Succesfully connected to SMTP server!')

        print('Starting TLS communication...')
        smtp.starttls(context=ssl.create_default_context())

        print('Logging in...')
        smtp.login(sender, password)
        print('Login successful!')

        # Send emails.
        try:
          for s in range(len(santas)):
            santa = santas[s]
            receiver = santas[(s + 1) % len(santas)]

            message = EmailMessage()
            message['Subject'] = SUBJECT
            message['From'] = sender
            message['To'] = santa['email']
            message.set_content(BODY.format(santa=santa['name'], receiver=receiver['name']))

            print(f'Sending e-mail to {santa["name"]}, {santa["email"]}...')
            smtp.sendmail(sender, santa['email'], message.as_string())
        except Exception as e:
          eprint(e)
          print(f'Error sending e-mail to {santa["name"]}, {santa["email"]}...')
      break
    except Exception as e:
      i += 1
      eprint(e)
      print(f'Something went wrong, re-connecting to SMTP server (attempt {i})')


if __name__ == '__main__':
  if (len(sys.argv) != 3):
    print(f'Usage: {sys.argv[0]} <credentials.txt> <santas_file.csv>')
    sys.exit(-1)

  # Parse credentials
  sender, password = parse_credentials(sys.argv[1])

  # Parse input
  santas = parse_santas(sys.argv[2])
  if not confirm_santas(santas):
    sys.exit(-1)

  # Randomly shuffle santas. Each santa gives to the one after and receives from the one before.
  random.shuffle(santas)

  # Save assignments in case an error occurs.
  with open(f'data/santa_assignments_{time.strftime("%Y-%m-%d_%Hh%Mm%S", time.gmtime())}.txt', 'w') as f:
    f.write(repr(santas))

  # Send emails
  # send_emails(santas, sender, password)
