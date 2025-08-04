#!/usr/bin/env python3
"""Create sample HTML files for testing."""

from pathlib import Path


def create_simple_page():
    """Create a simple HTML page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple HTML Page</title>
    <meta name="description" content="A simple HTML page for testing">
    <meta name="keywords" content="test, html, simple">
</head>
<body>
    <h1>Welcome to the Simple Page</h1>
    
    <p>This is a simple HTML page used for testing the HTML reader functionality.</p>
    
    <h2>Features</h2>
    <p>This page demonstrates basic HTML elements:</p>
    <ul>
        <li>Headings</li>
        <li>Paragraphs</li>
        <li>Lists</li>
        <li>Links</li>
    </ul>
    
    <p>Visit <a href="https://example.com">our website</a> for more information.</p>
</body>
</html>"""
    
    with open('simple_page.html', 'w') as f:
        f.write(html)
    print("Created: simple_page.html")


def create_complex_page():
    """Create a complex HTML page with various elements."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Complex HTML Document</title>
    <meta name="author" content="Test Author">
    <meta property="og:title" content="Complex HTML Document">
    <meta property="og:description" content="A complex HTML page with various elements">
    
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .highlight {
            background-color: yellow;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
        }
    </style>
    
    <script>
        // This script should be removed during processing
        function showAlert() {
            alert('This is a test');
        }
    </script>
</head>
<body>
    <header>
        <h1>Complex HTML Document</h1>
        <nav>
            <a href="#intro">Introduction</a> |
            <a href="#features">Features</a> |
            <a href="#code">Code Examples</a> |
            <a href="#data">Data Table</a>
        </nav>
    </header>
    
    <main>
        <section id="intro">
            <h2>Introduction</h2>
            <p>This document demonstrates various HTML elements and their proper extraction.</p>
            
            <blockquote>
                "The web is more a social creation than a technical one." - Tim Berners-Lee
            </blockquote>
        </section>
        
        <section id="features">
            <h2>HTML Features</h2>
            
            <h3>Text Formatting</h3>
            <p>HTML supports various text formatting options:</p>
            <ul>
                <li><strong>Bold text</strong> using the strong tag</li>
                <li><em>Italic text</em> using the em tag</li>
                <li><mark class="highlight">Highlighted text</mark> using the mark tag</li>
                <li><code>Inline code</code> using the code tag</li>
                <li><small>Small text</small> using the small tag</li>
            </ul>
            
            <h3>Ordered Lists</h3>
            <ol>
                <li>First item</li>
                <li>Second item
                    <ol>
                        <li>Nested item 2.1</li>
                        <li>Nested item 2.2</li>
                    </ol>
                </li>
                <li>Third item</li>
            </ol>
        </section>
        
        <section id="code">
            <h2>Code Examples</h2>
            <p>Here's a Python code example:</p>
            
            <pre><code class="language-python">def fibonacci(n):
    "''Generate Fibonacci sequence up to n terms.''"
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Usage
for num in fibonacci(10):
    print(num)</code></pre>
        </section>
        
        <section id="data">
            <h2>Data Table</h2>
            <table border="1">
                <caption>Sample Data Table</caption>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Laptop</td>
                        <td>$999.99</td>
                        <td>15</td>
                        <td>Electronics</td>
                    </tr>
                    <tr>
                        <td>Mouse</td>
                        <td>$29.99</td>
                        <td>50</td>
                        <td>Accessories</td>
                    </tr>
                    <tr>
                        <td>Monitor</td>
                        <td>$299.99</td>
                        <td>8</td>
                        <td>Electronics</td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <section>
            <h2>Forms and Input</h2>
            <form action="/submit" method="post">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required><br><br>
                
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required><br><br>
                
                <label for="message">Message:</label><br>
                <textarea id="message" name="message" rows="4" cols="50"></textarea><br><br>
                
                <button type="submit">Submit</button>
            </form>
        </section>
    </main>
    
    <footer>
        <hr>
        <p>&copy; 2025 Test Company. All rights reserved.</p>
        <p>Contact: <a href="mailto:info@example.com">info@example.com</a></p>
    </footer>
    
    <!-- This is a comment that should be removed -->
</body>
</html>"""
    
    with open('complex_page.html', 'w') as f:
        f.write(html)
    print("Created: complex_page.html")


def create_blog_post():
    """Create a blog post style HTML."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Understanding Machine Learning - Tech Blog</title>
    <meta name="author" content="Jane Doe">
    <meta name="date" content="2025-01-15">
    <meta name="category" content="Technology, AI">
</head>
<body>
    <article>
        <header>
            <h1>Understanding Machine Learning: A Beginner's Guide</h1>
            <p class="meta">
                By <span class="author">Jane Doe</span> | 
                <time datetime="2025-01-15">January 15, 2025</time> | 
                <span class="reading-time">5 min read</span>
            </p>
        </header>
        
        <section class="introduction">
            <p class="lead">Machine Learning (ML) has become one of the most transformative technologies of our time. But what exactly is it, and how does it work?</p>
        </section>
        
        <section>
            <h2>What is Machine Learning?</h2>
            <p>Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Instead of following pre-written rules, ML algorithms find patterns in data and make decisions based on those patterns.</p>
            
            <figure>
                <img src="ml-diagram.png" alt="Machine Learning Process Diagram">
                <figcaption>The typical machine learning workflow</figcaption>
            </figure>
        </section>
        
        <section>
            <h2>Types of Machine Learning</h2>
            
            <h3>1. Supervised Learning</h3>
            <p>In supervised learning, the algorithm learns from labeled training data. Common applications include:</p>
            <ul>
                <li>Email spam detection</li>
                <li>Image classification</li>
                <li>Sales forecasting</li>
            </ul>
            
            <h3>2. Unsupervised Learning</h3>
            <p>Unsupervised learning works with unlabeled data to discover hidden patterns. Examples include:</p>
            <ul>
                <li>Customer segmentation</li>
                <li>Anomaly detection</li>
                <li>Recommendation systems</li>
            </ul>
            
            <h3>3. Reinforcement Learning</h3>
            <p>This type involves an agent learning to make decisions by receiving rewards or penalties. It's used in:</p>
            <ul>
                <li>Game playing (like Chess or Go)</li>
                <li>Robotics</li>
                <li>Autonomous vehicles</li>
            </ul>
        </section>
        
        <section>
            <h2>Real-World Applications</h2>
            <p>Machine learning is everywhere in our daily lives:</p>
            
            <dl>
                <dt><strong>Healthcare</strong></dt>
                <dd>Disease diagnosis, drug discovery, personalized treatment plans</dd>
                
                <dt><strong>Finance</strong></dt>
                <dd>Fraud detection, risk assessment, algorithmic trading</dd>
                
                <dt><strong>Retail</strong></dt>
                <dd>Product recommendations, demand forecasting, price optimization</dd>
            </dl>
        </section>
        
        <section>
            <h2>Getting Started with ML</h2>
            <p>If you're interested in learning machine learning, here's a simple Python example using scikit-learn:</p>
            
            <pre><code># Simple linear regression example
from sklearn.linear_model import LinearRegression
import numpy as np

# Training data
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])

# Create and train model
model = LinearRegression()
model.fit(X, y)

# Make prediction
prediction = model.predict([[6]])
print(f"Prediction for x=6: {prediction[0]}")</code></pre>
        </section>
        
        <section class="conclusion">
            <h2>Conclusion</h2>
            <p>Machine learning is a powerful tool that's reshaping industries and creating new possibilities. While it may seem complex at first, with the right resources and dedication, anyone can start their journey into this exciting field.</p>
            
            <p>Remember, the key to mastering ML is practice and continuous learning. Start small, experiment with different algorithms, and gradually work your way up to more complex problems.</p>
        </section>
        
        <aside class="related-posts">
            <h3>Related Articles</h3>
            <ul>
                <li><a href="/deep-learning-basics">Deep Learning Basics</a></li>
                <li><a href="/python-for-data-science">Python for Data Science</a></li>
                <li><a href="/ai-ethics">The Ethics of AI</a></li>
            </ul>
        </aside>
    </article>
</body>
</html>"""
    
    with open('blog_post.html', 'w') as f:
        f.write(html)
    print("Created: blog_post.html")


def create_malformed_html():
    """Create a malformed HTML file to test error handling."""
    html = """<html>
<head>
    <title>Malformed HTML Test
</head>
<body>
    <h1>This HTML has issues</h1>
    
    <p>Unclosed paragraph tag
    
    <div>
        <p>Nested but not properly closed
        <span>More nesting issues
    </div>
    
    <!-- Broken comment -- >
    
    <table>
        <tr>
            <td>Cell without closing tags
            <td>Another cell
        <tr>
            <td>New row
    </table>
    
    <script>
        // Unclosed script
        var x = "test
    
    Random text outside any tags
    
    <p>Final paragraph</p>
</body>"""
    
    with open('malformed.html', 'w') as f:
        f.write(html)
    print("Created: malformed.html")


def create_minimal_html():
    """Create a minimal HTML file."""
    html = """<html>
<body>
<p>Minimal HTML content</p>
</body>
</html>"""
    
    with open('minimal.html', 'w') as f:
        f.write(html)
    print("Created: minimal.html")


def main():
    """Create all sample HTML files."""
    print("Creating sample HTML files...")
    
    # Change to the html directory
    html_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(html_dir)
        
        create_simple_page()
        create_complex_page()
        create_blog_post()
        create_malformed_html()
        create_minimal_html()
        
        print("\nAll sample HTML files created successfully!")
        print(f"Files created in: {html_dir}")
        
    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()