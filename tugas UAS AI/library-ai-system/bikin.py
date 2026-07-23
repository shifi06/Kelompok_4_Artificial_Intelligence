import csv
import random

def generate_dummy_dataset():
    categories = ['AI', 'Cybersecurity', 'Programming', 'HTML', 'CSS', 'JavaScript', 'Python', 'Engineering', 'Data']
    
    first_names = ['John', 'Jane', 'Alex', 'Sarah', 'Michael', 'Emily', 'David', 'Laura', 'Robert', 'Emma']
    last_names = ['Smith', 'Doe', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris']
    
    prefixes = ['Mastering', 'The Art of', 'Introduction to', 'Advanced', 'Practical', 'Fundamentals of', 'Modern']
    suffixes = ['for Beginners', 'in Practice', 'Handbook', 'Demystified', 'Step by Step', 'for Professionals']
    
    filename = 'dataset_tech_900.csv'
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Sesuai header yang sudah dikenali oleh sistemmu
        writer.writerow(['Title', 'Author', 'Category', 'Pages', 'Synopsis'])
        
        for category in categories:
            for i in range(1, 101):
                # Generate Judul Acak
                prefix = random.choice(prefixes)
                suffix = random.choice(suffixes)
                if random.random() > 0.5:
                    title = f"{prefix} {category}"
                else:
                    title = f"{category} {suffix}"
                
                # Generate Penulis, Halaman, & Sinopsis Acak
                author = f"{random.choice(first_names)} {random.choice(last_names)}"
                pages = random.randint(150, 800)
                synopsis = f"Buku panduan komprehensif ini membahas konsep-konsep penting tentang {category}. Cocok untuk pembaca yang ingin memperdalam wawasan mengenai {title}."
                
                writer.writerow([title, author, category, f"{pages} Halaman", synopsis])
                
    print(f"✅ Berhasil membuat file {filename} dengan total 900 buku!")

if __name__ == "__main__":
    generate_dummy_dataset()