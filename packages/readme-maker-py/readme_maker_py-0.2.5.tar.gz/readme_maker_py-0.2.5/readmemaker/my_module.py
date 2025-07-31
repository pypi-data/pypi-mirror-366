import argparse
from github import Github
import os
import nbformat
from nbconvert import PythonExporter
from groq import Groq

basic_markdown = """
Basic Syntax

These are the elements outlined in John Gruber’s original design document. All Markdown applications support these elements.
Element 	Markdown Syntax
Heading 	# H1
## H2
### H3
Bold 	**bold text**
Italic 	*italicized text*
Blockquote 	> blockquote
Ordered List 	1. First item
2. Second item
3. Third item
Unordered List 	- First item
- Second item
- Third item
Code 	`code`
Horizontal Rule 	---
Link 	[title](https://www.example.com)
Image 	![alt text](image.jpg)
Extended Syntax

These elements extend the basic syntax by adding additional features. Not all Markdown applications support these elements.
Element 	Markdown Syntax
Table 	| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |
Fenced Code Block 	```
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```
Footnote 	Here's a sentence with a footnote. [^1]

[^1]: This is the footnote.
Heading ID 	### My Great Heading {#custom-id}
Definition List 	term
: definition
Strikethrough 	~~The world is flat.~~
Task List 	- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media
Emoji
(see also Copying and Pasting Emoji) 	That is so funny! :joy:
Highlight 	I need to highlight these ==very important words==.
Subscript 	H~2~O
Superscript 	X^2^
"""

demo_readme = """
# 🎓 College Compus
  
  *Your Academic Compass in the Campus* 
  
[![Next.js](https://img.shields.io/badge/Built%20with-Next.js-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=websocket&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![GROQ](https://img.shields.io/badge/GROQ-F06835?style=for-the-badge&logo=sanity&logoColor=white)](https://www.sanity.io/docs/groq)
[![Qdrant](https://img.shields.io/badge/Qdrant-E94D33?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Next.js 15](https://img.shields.io/badge/Next.js%2015-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)](https://www.openstreetmap.org/)
[![LiveKit](https://img.shields.io/badge/LiveKit-4537DE?style=for-the-badge&logo=livekit&logoColor=white)](https://livekit.io/)

</div>

## 🌟 Overview

College Compus is your all-in-one college companion, developed for the ACM Ideathon at Punjab Engineering College. Our platform revolutionizes campus life by integrating academic management, social connections, and real-time location services into a seamless experience.

### 🏆 Ideathon Project
- **Event**: ACM Ideathon 2024
- **Institution**: Punjab Engineering College
- **Team Members**: 
  - Vaibhav Verma
  - Mrinal Gaur
  - Antriksh Gupta
  - Prajanya Sharma

## ✨ Features

### 📚 Academic Management
- **Grade Tracking**: Monitor and analyze academic performance
- **Online Classes**: Virtual learning environment with interactive whiteboard
- **Study Requests**: Connect with senior students for paid tutoring sessions

### 🎯 Campus Life
- **Club Management**: Join and manage college clubs and societies
- **Event Calendar**: Stay updated with campus events and activities
- **Issues Panel**: Report and track campus-related concerns

### 🤝 Social Features
- **Friends System**: Connect with fellow students
- **Real-time Location**: Find friends on campus ([MapImplement Repository](https://github.com/mrinalgaur2005/MapImplement))
- **Study Groups**: Create and join study sessions

### 🎨 Interactive Features
- **Interactive Whiteboard**: Real-time collaborative drawing and teaching
- **Live Chat**: Instant messaging during online classes
- **Resources**: Page for Teachers and Seniors to share resources with students

### 🤖 AI Chat Bot
- Interactive Chatbot which helps you in your day to day activity as well as navigating the entire website in one click!.
- Features it can help you with
  * Ask your marks and get precise results.
  * Ask for events happening in college.
  * Ask for general info about college or website.


## 🛠️ Tech Stack

- **Frontend**: Next.js 15, TailwindCSS, Socket.io-client,
- **Backend**: Node.js, Express.js, Websocket, Groq AI
- **Database**: MongoDB, Qdrant Vector DB, Redis
- **Authentication**: JWT, NextAuth.js, NodeMailer, Tesseract
- **Maps**: OpenStreetMap
- **Real-time**: WebSocket, Livekit

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/VaibhavVerma27/Ideathon

# Install dependencies
cd college-compus
npm install

# Set up environment variables
cp .env

# Run the development server
npm run dev
```

## 🔗 API Documentation

# Backend API Routes

Access the entire backend api routes through this [Pastebin Link](https://pastebin.com/Dxr20v9E)

# Frontend API Routes

- `/`: Home Page
- `/events`: Events page
- `/events/add-event`: page to add Events
- `/events/edit-event`: page to edit existing Events
- `/events/[...eventId]`: Single Event info page
- `/MAP`: Map page
- `/clubs`: Clubs page
- `/clubs/[...clubId]`: Single Club info page
- `/issues`: Issues page
- `/issues/add-issues`: Add Issues page
- `/issues/edit-issues`: page to edit your Issues
- `/issues/my-issues`: page to list your Issues
- `/user/friends`: Friends page
- `/study-requests`: Study-Requests Page
- `/resources`: Resources page
- `/dashboard/student`: Student Dashboard page
- `/dashboard/teacher`: Teacher Dashboard page
- `/admin/announcements/add`: Add announcement page for ADMINS
- `/admin/clubs/add-club`: Add Club page for ADMINS
- `/admin/subjects/teacher`: Add/Remove subjects from Teacher page
- `/admin/subjects/teacher`: Add/Remove subjects from Students page
- `/admin/user/make-admin`: page for an Admin to add other user as Admin
- `/admin/user/make-teacher`: page for an Admin to enroll an User as Teacher
- `/study-room/[...roomId]`: Connect to rooms with your teachers or Seniors and study with them.

## 📱 Screenshots

<div align="center">
  <img src="images/Screenshot_20250114_003732.png/" alt="Home" width="800"/>
  <img src="images/Screenshot_20250114_003900.png" alt="Clubs" width="800"/>
  <img src="images/Screenshot_20250114_003945.png" alt="Dashbaord" width="800"/>
</div>

## 🙏 Acknowledgments

- Punjab Engineering College
- ACM Student Chapter
- Our mentors and professors
---

<div align="center">
  Made with ❤️ by PEC Students
  
  [Website]([https://college-compus.vercel.app](https://pec.ac.in/)) · [Report Bug](https://github.com/VaibhavVerma27/Ideathon/issues) · [Request Feature](https://github.com/VaibhavVerma27/Ideathon/issues)
</div>
"""


def convert_notebook_to_script(notebook_content):
    notebook_node = nbformat.reads(notebook_content, as_version=4)
    exporter = PythonExporter()
    script_content, _ = exporter.from_notebook_node(notebook_node)
    return script_content

def get_bot_response(text, file_name, groq_client):
    original_extension = os.path.splitext(file_name)[1]
    if not original_extension and '_' in file_name:
        parts = file_name.split('_')
        if len(parts) > 0:
            original_extension = '.' + parts[0]
    
    detailed_prompt = f"""I am making a GitHub readme file maker. I will provide you with code from a {original_extension} file, and I need you to write a 100-200 word description for that code. 

    Here is the code of the file: {text}

    Make sure you cover:
    1. What programming language this is
    2. Any module packages or libraries used
    3. The primary purpose of the code
    4. Key functionalities 

    I will combine all descriptions to generate a final readme file. Focus only on describing this specific file's code. Keep your response between 100-200 words. If you feel like a file doesnt provide much information about the project, then simply return an empty text"""

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": detailed_prompt}
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1000
    )

    return chat_completion.choices[0].message.content

def get_bot_response_readme(text, groq_client, additional_info, basic_markdown, demo_readme):
    detailed_prompt = f"""I am giving you brief descriptions about each code file in my project. Please create a comprehensive GitHub README.md file using all this information.

    Here are the file descriptions: {text}

    The README should include:
    1. Project title and brief overview
    2. Installation instructions
    3. Usage examples
    4. Code explanations with appropriate code snippets
    5. Project structure
    6. Dependencies

    Format the README with proper Markdown syntax including headers, code blocks, lists, etc. Make it professional, complete, and easy to understand for developers of any level. Add several emojis and proper formatting of text to make it more visually appealing, like adding bold text, italics, headers, etc. Make sure the read me file is visually appealing and easy to read. I am providing you with some syntax examples of markdown language, make sure you use them to make more visually aesthetic. Here it is {basic_markdown}. This is what a demo readme file looks like, you can use this as a reference: {demo_readme}, make sure you stay very close to this.Components like this [![Next.js](https://img.shields.io/badge/Built%20with-Next.js-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
    looks good in the readme file, so make sure you add them. This is additional information you NEED to add to the readme file: {additional_info}"""

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": detailed_prompt}
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=10000
    )

    return chat_completion.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='Generate a README.md file for a GitHub repository.')
    parser.add_argument('-r', '--repo', required=True, help='GitHub repository in the format "owner/repo"')
    parser.add_argument('-k', '--key', required=True, help='Groq API key')
    args = parser.parse_args()

    g = Github()
    repo = g.get_repo(args.repo)

    additional_info = input("Do you want to add any additional information to the README? (y/n): ")
    if additional_info.lower() == 'y':
        additional_info = input("Enter the additional information you want to add: ")
        with open(r'additional_info_ai.txt', 'w', encoding='utf-8') as additional_info_file:
            additional_info_file.write(additional_info)

    ignored_these_files = [
    # Documentation files
    "README.md", "README.txt", "README.rst", "README", "CHANGELOG.md", "CHANGELOG.txt", 
    "HISTORY.md", "NEWS.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
    "AUTHORS.md", "CONTRIBUTORS.md", "MAINTAINERS.md", "ACKNOWLEDGMENTS.md",

    # License files
    "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "UNLICENSE",
    
    # Git files
    ".gitignore", ".gitattributes", ".gitmodules", ".gitkeep",
    
    # GitHub files
    ".github", "ISSUE_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md",
    
    # Package manager files
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Pipfile", "Pipfile.lock", "poetry.lock", "requirements.txt", "requirements-dev.txt",
    "Gemfile", "Gemfile.lock", "composer.json", "composer.lock",
    
    # Node.js / JavaScript config files
    ".eslintrc.json", ".eslintrc.js", ".eslintrc.yml", ".eslintrc.yaml",
    ".prettierrc", ".prettierrc.json", ".prettierrc.js", ".prettierignore",
    "next.config.js", "next.config.mjs", "next.config.ts",
    "webpack.config.js", "vite.config.js", "rollup.config.js",
    "babel.config.js", ".babelrc", ".babelrc.json",
    "postcss.config.js", "postcss.config.mjs",
    "tailwind.config.js", "tailwind.config.ts",
    "tsconfig.json", "jsconfig.json",
    "components.json", "deploy.yml",
    
    # Python config files
    "setup.py", "setup.cfg", "pyproject.toml", "MANIFEST.in",
    "tox.ini", "pytest.ini", ".coveragerc", "mypy.ini",
    
    # Editor and IDE files
    ".vscode", ".idea", "*.sublime-project", "*.sublime-workspace",
    ".editorconfig",
    
    # OS files
    ".DS_Store", "Thumbs.db", "desktop.ini",
    
    # Docker files
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore",
    
    # CI/CD files
    ".travis.yml", ".circleci", "appveyor.yml", ".gitlab-ci.yml",
    "azure-pipelines.yml", "Jenkinsfile",
    
    # Environment files
    ".env", ".env.local", ".env.development", ".env.production", ".env.example",
    
    # Cache and temporary files
    "node_modules", ".cache", ".tmp", ".temp",
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    ".pytest_cache", ".coverage", "htmlcov",
    
    # Build output directories
    "dist", "build", "out", ".next", ".nuxt",

    # Java / Spring Boot specific build output
    "target", "*.class", "*.jar", "*.war", "*.iml",

    # Spring Boot specific config and boilerplate
    "application.properties", "application.yml", "application.yaml",
    "application-dev.properties", "application-prod.properties",
    "application-test.properties", "application-local.properties",
    ".mvn", "mvnw", "mvnw.cmd", "pom.xml",
    "gradlew", "gradlew.bat", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",

    # Log files
    "*.log", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
    
    # Lock files and dependency logs
    "yarn-error.log", "lerna-debug.log",
    
    # Other common config files
    ".nvmrc", ".ruby-version", ".python-version", ".node-version",
    "Makefile", "makefile", "CMakeLists.txt",
    ".clang-format", ".clang-tidy",

    # Redundant/dupes
    "vite.config.js", "tailwind.config.js", "eslint.config.js",
]


    groq_client = Groq(api_key=args.key)
    folder_path = r"Readme Maker"
    outside_path = os.path.join(os.getcwd())
    output_folder = folder_path
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    code_extensions = [
        '.py', '.ipynb',
        '.html', '.css', '.js', '.jsx', '.ts', '.tsx',
        '.c', '.cpp', '.h', '.hpp', '.cs',
        '.java', '.kt',
        '.rb', '.php', '.go',
        '.rs', '.swift',
        '.sh', '.bash',
        '.r', '.scala', '.lua', '.pl', '.sql'
    ]

    contents = repo.get_contents("") 

    while contents:
        file_content = contents.pop(0)

        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path)) 

        else:
            # Check if the filename should be ignored
            filename = os.path.basename(file_content.path)
            if filename in ignored_these_files:
                print(f"Skipping ignored file: {filename}")
                continue
                
            file_extension = os.path.splitext(file_content.path)[1].lower()

            if file_extension in code_extensions:
                if file_extension == '.ipynb':
                    try:
                        notebook_content = file_content.decoded_content.decode("utf-8")
                        python_script = convert_notebook_to_script(notebook_content)

                        output_basename = os.path.basename(file_content.path).replace('.ipynb', '')
                        python_file_path = os.path.join(output_folder, output_basename + '.py')
                        with open(python_file_path, 'w', encoding='utf-8') as py_file:
                            py_file.write(python_script)

                        text_file_path = os.path.join(output_folder, output_basename + '.txt')
                        with open(text_file_path, 'w', encoding='utf-8') as text_file:
                            text_file.write(python_script)
                    except Exception as e:
                        print(f"Error processing notebook {file_content.path}: {e}")
                else:
                    try:
                        file_content_text = file_content.decoded_content.decode("utf-8")
                        output_basename = os.path.basename(file_content.path)
                        text_file_path = os.path.join(output_folder, output_basename.replace(file_extension, '.txt'))

                        with open(text_file_path, 'w', encoding='utf-8') as text_file:
                            text_file.write(file_content_text)
                    except UnicodeDecodeError:
                        print(f"Could not decode {file_content.path} as UTF-8, skipping")
                    except Exception as e:
                        print(f"Error processing {file_content.path}: {e}")

    while True:
        text_files = [f for f in os.listdir(folder_path) if f.endswith('.txt') and not f.endswith('_ai.txt')]
        
        for text_file in text_files:
            text_file_path = os.path.join(folder_path, text_file)
            
            with open(text_file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
            
            response = get_bot_response(text_content, text_file, groq_client)
            
            text_file_base = text_file.replace('.txt', '')
            ai_text_file_path = os.path.join(folder_path, f"{text_file_base}_ai.txt")
            with open(ai_text_file_path, 'w', encoding='utf-8') as ai_file:
                ai_file.write(f"Response for {text_file}:\n{response}\n\n")
        break

    all_text = ""

    for file_name in os.listdir(folder_path):
        if file_name.endswith('_ai.txt'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                all_text += file.read() + "\n"

    final_response = get_bot_response_readme(all_text, groq_client, additional_info, basic_markdown, demo_readme)

    readme_path = os.path.join(outside_path, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.write(final_response)

    print(f"README.md has been created at {readme_path}")

if __name__ == "__main__":
    main()