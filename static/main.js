// Tooltips para reações do BBB
document.addEventListener('DOMContentLoaded', function() {
    const reactionData = {
        '❤️': 'Indica afeto ou amizade',
        '💔': 'Expressa decepção ou mágoa',
        '🎯': 'Sinaliza que o participante é considerado um adversário ou está na mira para votos',
        '🐍': 'Sugere traição ou falsidade',
        '🧳': 'Aponta que o participante é visto como chato ou inconveniente',
        '🍪': 'Indica que o participante busca atenção ou reconhecimento',
        '🤮': 'Demonstra repulsa ou desaprovação',
        '🤥': 'Acusa o participante de falta de sinceridade',
        '🌱': 'Refere-se a alguém considerado apagado ou sem participação ativa no jogo'
    };

    // Adiciona tooltips dinâmicos
    document.querySelectorAll('select[name="reaction"]').forEach(select => {
        select.addEventListener('change', function() {
            const selectedValue = this.options[this.selectedIndex].value;
            this.title = reactionData[selectedValue] || '';
        });

        // Mostra tooltip ao passar o mouse
        select.addEventListener('mouseover', function() {
            if (!this.title) {
                const selectedValue = this.options[this.selectedIndex].value;
                this.title = reactionData[selectedValue] || '';
            }
        });
    });

    // Melhoria: Exibe emojis maiores no dropdown
    const style = document.createElement('style');
    style.textContent = `
        select[name="reaction"] option {
            font-size: 1.4em;
            padding: 8px 12px;
        }
        select[name="reaction"] option[value=""] {
            font-size: 1em;
        }
    `;
    document.head.appendChild(style);
});
