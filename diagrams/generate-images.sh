#!/bin/bash

# Script to generate image files from Mermaid diagrams
# Requires @mermaid-js/mermaid-cli to be installed: npm install -g @mermaid-js/mermaid-cli

echo "🏥 MedLitBot - Diagram Image Generator"
echo "======================================"

# Check if mermaid CLI is installed
if ! command -v mmdc &> /dev/null; then
    echo "❌ Error: Mermaid CLI not found!"
    echo "📦 Install it with: npm install -g @mermaid-js/mermaid-cli"
    echo "🔗 Or use the online editor: https://mermaid.live/"
    exit 1
fi

echo "✅ Mermaid CLI found, generating images..."
echo ""

# Create output directories
mkdir -p png svg pdf

# Generate PNG images (for presentations, documents)
echo "🖼️  Generating PNG images..."
mmdc -i 01-system-architecture.mmd -o png/01-system-architecture.png -b white -w 1920 -H 1080
mmdc -i 02-process-flow.mmd -o png/02-process-flow.png -b white -w 1920 -H 1080  
mmdc -i 03-technology-stack.mmd -o png/03-technology-stack.png -b white -w 1920 -H 1080

# Generate SVG images (scalable, best for web)
echo "🎨 Generating SVG images..."
mmdc -i 01-system-architecture.mmd -o svg/01-system-architecture.svg -b white
mmdc -i 02-process-flow.mmd -o svg/02-process-flow.svg -b white
mmdc -i 03-technology-stack.mmd -o svg/03-technology-stack.svg -b white

# Generate PDF images (for printing, documentation)
echo "📄 Generating PDF images..."
mmdc -i 01-system-architecture.mmd -o pdf/01-system-architecture.pdf -b white
mmdc -i 02-process-flow.mmd -o pdf/02-process-flow.pdf -b white  
mmdc -i 03-technology-stack.mmd -o pdf/03-technology-stack.pdf -b white

echo ""
echo "🎉 Image generation complete!"
echo ""
echo "📁 Generated files:"
echo "   📂 png/     - PNG images (1920x1080, good for presentations)"
echo "   📂 svg/     - SVG images (scalable, perfect for web)"  
echo "   📂 pdf/     - PDF images (vector, great for printing)"
echo ""
echo "💡 To view diagrams in your browser:"
echo "   👀 Open: view-diagrams.html"
echo ""
echo "📚 For more info, see: README.md"
