import argparse
import json
import requests
import smtplib
import ssl


def email_jobs(jobs, receivers):

    listings = []

    for job in jobs:

        company = job['company']
        position = job['position']
        tags = job['tags']
        url = job['url']

        listings.append(f'Company: {company}\nPosition: {position}\nTags: {tags}\nURL: {url}')

    message = 'Subject: Remote Job Listings\n' + '\n\n'.join(listings)

    import getpass

    port = 465
    password = getpass.getpass()

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:

        server.login("remote.job.listings@gmail.com", password)

        sender_email = "remote.job.listings@gmail.com"

        for receiver in receivers:

            server.sendmail(sender_email, receiver, message)


def filter_by_tags(jobs, tags):

    return [job for job in jobs if not set(tags).isdisjoint(job['tags'])]


def filter_by_date(jobs, date):

    from datetime import datetime

    date_mask = '%Y-%m-%d'
    cutoff_date = datetime.strptime(date, date_mask)

    filtered_jobs = []

    for job in jobs:

        job_date = datetime.strptime(job['date'].split('T')[0], date_mask)

        if job_date > cutoff_date:

            filtered_jobs.append(job)

    return filtered_jobs


def remote_jobs(tags=None):

    r = requests.get('https://remoteok.io/api?ref=producthunt')

    return r.json()[1:]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--tags", nargs='+', help="search by tags")
    parser.add_argument("-d", "--date", type=str, help="search by date")
    parser.add_argument("-e", "--emails", nargs='+', help="receiver emails")
    parser.add_argument("--output", dest="output", action="store_true", help="dump output to JSON")

    args = parser.parse_args()

    print('Fetching remote job listings...')
    jobs = remote_jobs()
    print(f'Received {len(jobs)} remote job listings.')

    if args.tags:

        print(f'Filtering jobs by tags: {args.tags}')
        jobs = filter_by_tags(jobs, args.tags)
        print(f'{len(jobs)} jobs match the filter.')

    if args.date:

        print(f'Filtering jobs by date: {args.date}')
        jobs = filter_by_date(jobs, args.date)
        print(f'{len(jobs)} jobs match the filter.')

    if args.emails:

        email_jobs(jobs, args.emails)

    if args.output:

        print(json.dumps(jobs, indent=4))
