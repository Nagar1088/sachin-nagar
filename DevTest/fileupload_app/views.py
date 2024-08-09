from django.core.mail import send_mail
from django.shortcuts import render
from .forms import UploadFileForm
import os
import pandas as pd
from django.conf import settings

def handle_uploaded_file(f):
    directory = 'media'
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path

def generate_summary_report(file_path):
    df = pd.read_excel(file_path)
    summary = {
        'Number of Rows': df.shape[0],
        'Number of Columns': df.shape[1],
        'Columns': df.columns.tolist(),
        'Data Types': df.dtypes.to_dict(),
        'Summary Statistics': df.describe().to_dict()
    }
    return summary

def send_summary_email(summary, recipient_list):
    subject = 'Python Assignment - Sachin Nagar'
    body = (
        f"Summary Report:\n\n"
        f"Number of Rows: {summary['Number of Rows']}\n"
        f"Number of Columns: {summary['Number of Columns']}\n"
        f"Columns: {', '.join(summary['Columns'])}\n"
        f"Data Types:\n" + "\n".join([f"{col}: {dtype}" for col, dtype in summary['Data Types'].items()]) + "\n\n"
        f"Summary Statistics:\n"
        + "\n".join([f"{stat}:\n" + "\n".join([f"  {col}: {value}" for col, value in values.items()]) for stat, values in summary['Summary Statistics'].items()])
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES['file'])
            summary = generate_summary_report(file_path)

            # List of email addresses to send the summary
            recipient_list = ['recipient1@example.com', 'recipient2@example.com']
            send_summary_email(summary, recipient_list)

            return render(request, 'fileupload_app/success.html', {
                'file_path': file_path,
                'summary': summary
            })
    else:
        form = UploadFileForm()

    return render(request, 'fileupload_app/upload.html', {'form': form})
