import random
from django.core.management.base import BaseCommand
from quizzes.models import Category, Subcategory, Question, Choice

class Command(BaseCommand):
    help = 'Seeds all 12 subcategories with 15 real questions (5 per difficulty)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Wiping old data...")
        Category.objects.all().delete()

        # MASTER DATA BANK (5 Questions per Level)
        data_bank = {
            # --- ACADEMIC ---
            'Physics': {
                'Easy': [
                    {'q': 'What is the SI unit of force?', 'a': 'Newton', 'w': ['Joule', 'Watt', 'Volt']},
                    {'q': 'What is the boiling point of water?', 'a': '100°C', 'w': ['0°C', '50°C', '200°C']},
                    {'q': 'Which state of matter has a definite shape?', 'a': 'Solid', 'w': ['Liquid', 'Gas', 'Plasma']},
                    {'q': 'Which instrument measures atmospheric pressure?', 'a': 'Barometer', 'w': ['Thermometer', 'Voltmeter', 'Ammeter']},
                    {'q': 'What is the primary source of energy for Earth?', 'a': 'Sun', 'w': ['Moon', 'Wind', 'Coal']},
                ],
                'Medium': [
                    {'q': 'What is the speed of light?', 'a': '3x10^8 m/s', 'w': ['3x10^6 m/s', '1500 m/s', '343 m/s']},
                    {'q': 'Unit of electrical resistance?', 'a': 'Ohm', 'w': ['Volt', 'Ampere', 'Watt']},
                    {'q': 'Who discovered the Electron?', 'a': 'J.J. Thomson', 'w': ['Einstein', 'Rutherford', 'Bohr']},
                    {'q': 'What type of lens is used to correct myopia?', 'a': 'Concave', 'w': ['Convex', 'Bifocal', 'Cylindrical']},
                    {'q': 'Refractive index of a vacuum is?', 'a': '1.0', 'w': ['0.0', '1.33', '1.5']},
                ],
                'Hard': [
                    {'q': 'What is the escape velocity of Earth?', 'a': '11.2 km/s', 'w': ['9.8 km/s', '42 km/s', '5.5 km/s']},
                    {'q': 'Value of Planck constant?', 'a': '6.626x10^-34 J·s', 'w': ['1.6x10^-19', '9.1x10^-31', '3.14']},
                    {'q': 'Which principle explains aircraft lift?', 'a': 'Bernoulli', 'w': ['Pascal', 'Archimedes', 'Newton']},
                    {'q': 'The half-life of Carbon-14 is approx?', 'a': '5730 years', 'w': ['1000 years', '10000 years', '500 years']},
                    {'q': 'What is the unit of magnetic flux?', 'a': 'Weber', 'w': ['Tesla', 'Henry', 'Farad']},
                ]
            },
            'Chemistry': {
                'Easy': [
                    {'q': 'Chemical symbol for Gold?', 'a': 'Au', 'w': ['Ag', 'Gd', 'Fe']},
                    {'q': 'What is the pH of pure water?', 'a': '7', 'w': ['1', '14', '10']},
                    {'q': 'Which gas do humans exhale?', 'a': 'Carbon Dioxide', 'w': ['Oxygen', 'Nitrogen', 'Argon']},
                    {'q': 'What is the lightest element?', 'a': 'Hydrogen', 'w': ['Helium', 'Oxygen', 'Lithium']},
                    {'q': 'Formula for common salt?', 'a': 'NaCl', 'w': ['KCl', 'NaOH', 'HCl']},
                ],
                'Medium': [
                    {'q': 'Which metal is liquid at room temperature?', 'a': 'Mercury', 'w': ['Silver', 'Sodium', 'Lead']},
                    {'q': 'Main component of natural gas?', 'a': 'Methane', 'w': ['Ethane', 'Propane', 'Butane']},
                    {'q': 'Hardest natural substance?', 'a': 'Diamond', 'w': ['Gold', 'Iron', 'Quartz']},
                    {'q': 'Acid found in lemons?', 'a': 'Citric Acid', 'w': ['Acetic Acid', 'Lactic Acid', 'Nitric Acid']},
                    {'q': 'Process of losing electrons is?', 'a': 'Oxidation', 'w': ['Reduction', 'Hydrolysis', 'Ionization']},
                ],
                'Hard': [
                    {'q': 'Noble gas in Period 1?', 'a': 'Helium', 'w': ['Neon', 'Argon', 'Radon']},
                    {'q': 'Avogadro\'s number is?', 'a': '6.022x10^23', 'w': ['3.14x10^23', '9.1x10^-31', '1.6x10^-19']},
                    {'q': 'Most abundant metal in Earth\'s crust?', 'a': 'Aluminum', 'w': ['Iron', 'Gold', 'Silicon']},
                    {'q': 'Which catalyst is used in Haber process?', 'a': 'Iron', 'w': ['Platinum', 'Nickel', 'Copper']},
                    {'q': 'Bond formed by sharing electrons?', 'a': 'Covalent', 'w': ['Ionic', 'Hydrogen', 'Metallic']},
                ]
            },
            'Mathematics': {
                'Easy': [
                    {'q': 'Square root of 144?', 'a': '12', 'w': ['14', '10', '16']},
                    {'q': 'What is 15% of 200?', 'a': '30', 'w': ['20', '15', '45']},
                    {'q': 'Sum of angles in a triangle?', 'a': '180°', 'w': ['90°', '360°', '270°']},
                    {'q': 'First prime number?', 'a': '2', 'w': ['1', '3', '0']},
                    {'q': 'A polygon with 5 sides is a?', 'a': 'Pentagon', 'w': ['Hexagon', 'Octagon', 'Square']},
                ],
                'Medium': [
                    {'q': 'What is 7 cubed?', 'a': '343', 'w': ['243', '49', '512']},
                    {'q': 'Value of Pi (2 decimal)?', 'a': '3.14', 'w': ['3.12', '3.16', '3.18']},
                    {'q': 'A triangle with 3 equal sides?', 'a': 'Equilateral', 'w': ['Isosceles', 'Scalene', 'Right']},
                    {'q': 'Mode of [1,2,2,3,4]?', 'a': '2', 'w': ['1', '3', '4']},
                    {'q': 'How many degrees in a circle?', 'a': '360°', 'w': ['180°', '90°', '540°']},
                ],
                'Hard': [
                    {'q': 'Derivative of sin(x)?', 'a': 'cos(x)', 'w': ['-sin(x)', 'tan(x)', 'sec(x)']},
                    {'q': 'Sum of angles in a hexagon?', 'a': '720°', 'w': ['540°', '360°', '1080°']},
                    {'q': 'Solve for x: log10(x) = 2', 'a': '100', 'w': ['10', '20', '1000']},
                    {'q': 'Hypotenuse of triangle (sides 3, 4)?', 'a': '5', 'w': ['6', '7', '4']},
                    {'q': 'Pythagorean Theorem is?', 'a': 'a² + b² = c²', 'w': ['a + b = c', 'ab = c', 'a² - b² = c²']},
                ]
            },
            'Biology': {
                'Easy': [
                    {'q': 'Powerhouse of the cell?', 'a': 'Mitochondria', 'w': ['Nucleus', 'Ribosome', 'Golgi']},
                    {'q': 'Largest organ in the human body?', 'a': 'Skin', 'w': ['Liver', 'Heart', 'Brain']},
                    {'q': 'Green pigment in plants?', 'a': 'Chlorophyll', 'w': ['Melanin', 'Hemoglobin', 'Bile']},
                    {'q': 'How many bones in adult human body?', 'a': '206', 'w': ['300', '150', '250']},
                    {'q': 'Gas absorbed during photosynthesis?', 'a': 'Carbon Dioxide', 'w': ['Oxygen', 'Nitrogen', 'Methane']},
                ],
                'Medium': [
                    {'q': 'How many chambers in human heart?', 'a': '4', 'w': ['2', '3', '6']},
                    {'q': 'Normal human body temperature?', 'a': '37°C', 'w': ['32°C', '40°C', '35°C']},
                    {'q': 'Organ that filters blood?', 'a': 'Kidneys', 'w': ['Lungs', 'Stomach', 'Pancreas']},
                    {'q': 'Part of brain controlling balance?', 'a': 'Cerebellum', 'w': ['Cerebrum', 'Medulla', 'Thalamus']},
                    {'q': 'Vitamins made by sunlight?', 'a': 'Vitamin D', 'w': ['Vitamin C', 'Vitamin A', 'Vitamin K']},
                ],
                'Hard': [
                    {'q': 'Study of fungi?', 'a': 'Mycology', 'w': ['Virology', 'Zoology', 'Botany']},
                    {'q': 'Number of pairs of chromosomes?', 'a': '23', 'w': ['46', '22', '24']},
                    {'q': 'Smallest bone in human body?', 'a': 'Stapes', 'w': ['Femur', 'Radius', 'Ulna']},
                    {'q': 'Who discovered Penicillin?', 'a': 'Alexander Fleming', 'w': ['Louis Pasteur', 'Gregor Mendel', 'Darwin']},
                    {'q': 'Blood type "Universal Donor"?', 'a': 'O negative', 'w': ['AB positive', 'O positive', 'A negative']},
                ]
            },
            'Movies': {
                'Easy': [
                    {'q': 'Who played Iron Man?', 'a': 'Robert Downey Jr.', 'w': ['Chris Evans', 'Mark Ruffalo', 'Chris Pratt']},
                    {'q': 'Name of the land in Frozen?', 'a': 'Arendelle', 'w': ['Genovia', 'Narnia', 'Westeros']},
                    {'q': 'What color is the pill in Matrix?', 'a': 'Red', 'w': ['Blue', 'Green', 'Yellow']},
                    {'q': 'Woody is a character in which movie?', 'a': 'Toy Story', 'w': ['Cars', 'Shrek', 'Up']},
                    {'q': 'Highest grossing movie (unadjusted)?', 'a': 'Avatar', 'w': ['Endgame', 'Titanic', 'Star Wars']},
                ],
                'Medium': [
                    {'q': 'Director of Inception?', 'a': 'Christopher Nolan', 'w': ['Spielberg', 'Tarantino', 'Scorsese']},
                    {'q': 'Actor who won Oscar as Joker?', 'a': 'Heath Ledger', 'w': ['Joaquin Phoenix', 'Jack Nicholson', 'Jared Leto']},
                    {'q': 'Nakatomi Plaza is from which movie?', 'a': 'Die Hard', 'w': ['Speed', 'Lethal Weapon', 'Matrix']},
                    {'q': 'First feature-length animated film?', 'a': 'Snow White', 'w': ['Bambi', 'Pinocchio', 'Fantasia']},
                    {'q': 'Voice of Genie in Aladdin (1992)?', 'a': 'Robin Williams', 'w': ['Will Smith', 'Tom Hanks', 'Eddie Murphy']},
                ],
                'Hard': [
                    {'q': 'First movie to win Best Picture?', 'a': 'Wings', 'w': ['Metropolis', 'Sunrise', 'Jazz Singer']},
                    {'q': 'How many Oscars did Titanic win?', 'a': '11', 'w': ['9', '10', '12']},
                    {'q': 'Briefcase combo in Pulp Fiction?', 'a': '666', 'w': ['777', '123', '000']},
                    {'q': 'Rose\'s drawing in Titanic by?', 'a': 'James Cameron', 'w': ['DiCaprio', 'Winslet', 'Picasso']},
                    {'q': 'Highest grossing R-rated film?', 'a': 'Joker', 'w': ['Deadpool', 'Logan', 'Oppenheimer']},
                ]
            },
            'Music': {
                'Easy': [
                    {'q': 'Who is the King of Pop?', 'a': 'Michael Jackson', 'w': ['Elvis', 'Prince', 'Drake']},
                    {'q': 'How many strings on a standard guitar?', 'a': '6', 'w': ['4', '5', '12']},
                    {'q': 'Lead singer of Queen?', 'a': 'Freddie Mercury', 'w': ['David Bowie', 'Mick Jagger', 'John Lennon']},
                    {'q': 'Member of Beatles?', 'a': 'Paul McCartney', 'w': ['Elvis', 'Elton John', 'Bono']},
                    {'q': 'Genre of Bob Marley?', 'a': 'Reggae', 'w': ['Jazz', 'Blues', 'Rock']},
                ],
                'Medium': [
                    {'q': 'How many keys on a standard piano?', 'a': '88', 'w': ['76', '92', '84']},
                    {'q': 'Beethoven\'s 9th title?', 'a': 'Choral', 'w': ['Moonlight', 'Eroica', 'Pastoral']},
                    {'q': 'Who won first American Idol?', 'a': 'Kelly Clarkson', 'w': ['Carrie Underwood', 'Adam Lambert', 'Clay Aiken']},
                    {'q': 'What does "Fortissimo" mean?', 'a': 'Very Loud', 'w': ['Very Soft', 'Very Fast', 'Very Slow']},
                    {'q': 'Year MTV launched?', 'a': '1981', 'w': ['1975', '1985', '1990']},
                ],
                'Hard': [
                    {'q': 'Which composer was deaf?', 'a': 'Beethoven', 'w': ['Mozart', 'Bach', 'Vivaldi']},
                    {'q': 'Real name of Lady Gaga?', 'a': 'Stefani', 'w': ['Angelina', 'Madonna', 'Joanne']},
                    {'q': 'Only band to play all 7 continents?', 'a': 'Metallica', 'w': ['Coldplay', 'U2', 'Rolling Stones']},
                    {'q': 'Most streamed song on Spotify?', 'a': 'Blinding Lights', 'w': ['Shape of You', 'Starboy', 'Perfect']},
                    {'q': 'Woodstock festival year?', 'a': '1969', 'w': ['1967', '1971', '1975']},
                ]
            },
            'Gaming': {
                'Easy': [
                    {'q': 'Mario\'s brother?', 'a': 'Luigi', 'w': ['Wario', 'Yoshi', 'Bowser']},
                    {'q': 'Best selling game ever?', 'a': 'Minecraft', 'w': ['GTA V', 'Tetris', 'Fortnite']},
                    {'q': 'Yellow character in Pac-Man?', 'a': 'Pac-Man', 'w': ['Blinky', 'Inky', 'Clyde']},
                    {'q': 'Nintendo console released in 2017?', 'a': 'Switch', 'w': ['Wii U', 'GameCube', 'N64']},
                    {'q': 'Main character in Legend of Zelda?', 'a': 'Link', 'w': ['Zelda', 'Ganon', 'Navi']},
                ],
                'Medium': [
                    {'q': 'Zelda world name?', 'a': 'Hyrule', 'w': ['Azeroth', 'Skyrim', 'Tamriel']},
                    {'q': 'First console to use discs?', 'a': 'Sega CD', 'w': ['PlayStation', 'N64', 'Dreamcast']},
                    {'q': 'Name of Master Chief\'s AI?', 'a': 'Cortana', 'w': ['Siri', 'Alexa', 'GlaDOS']},
                    {'q': 'Year first PlayStation released?', 'a': '1994', 'w': ['1990', '1996', '2000']},
                    {'q': 'Mortal Kombat creator?', 'a': 'Ed Boon', 'w': ['Kojima', 'Miyamoto', 'Carmack']},
                ],
                'Hard': [
                    {'q': 'First video game ever made?', 'a': 'Tennis for Two', 'w': ['Pong', 'Pac-Man', 'Asteroids']},
                    {'q': 'Creator of Dark Souls?', 'a': 'Miyazaki', 'w': ['Kojima', 'Mikami', 'Nomura']},
                    {'q': 'Original name for Mario?', 'a': 'Jumpman', 'w': ['Plumber', 'Redman', 'Stache']},
                    {'q': 'Konami code start?', 'a': 'Up Up Down Down', 'w': ['A B A B', 'L R L R', 'Select Start']},
                    {'q': 'Half-Life protagonist?', 'a': 'Gordon Freeman', 'w': ['Master Chief', 'Doomguy', 'Snake']},
                ]
            },
            'Celebrities': {
                'Easy': [
                    {'q': 'Married to Beyonce?', 'a': 'Jay-Z', 'w': ['Kanye', 'Drake', 'Nas']},
                    {'q': 'Dwayne Johnson\'s stage name?', 'a': 'The Rock', 'w': ['Stone Cold', 'Triple H', 'John Cena']},
                    {'q': 'Reality star with "Skims"?', 'a': 'Kim Kardashian', 'w': ['Kylie', 'Khloe', 'Kourtney']},
                    {'q': 'Iron Man actor?', 'a': 'Robert Downey Jr.', 'w': ['Chris Evans', 'Chris Hemsworth', 'Tom Holland']},
                    {'q': 'Taylor Swift genre?', 'a': 'Pop', 'w': ['Jazz', 'Blues', 'Metal']},
                ],
                'Medium': [
                    {'q': 'Won first American Idol?', 'a': 'Kelly Clarkson', 'w': ['Carrie Underwood', 'Adam Lambert', 'Clay Aiken']},
                    {'q': 'Tom Cruise movie franchise?', 'a': 'Mission Impossible', 'w': ['Fast & Furious', '007', 'Bourne']},
                    {'q': 'Rihanna birthplace?', 'a': 'Barbados', 'w': ['Jamaica', 'USA', 'Trinidad']},
                    {'q': 'Angelina Jolie famous role?', 'a': 'Lara Croft', 'w': ['Wonder Woman', 'Black Widow', 'Catwoman']},
                    {'q': 'Founder of Tesla?', 'a': 'Elon Musk', 'w': ['Jeff Bezos', 'Bill Gates', 'Tim Cook']},
                ],
                'Hard': [
                    {'q': 'Meryl Streep Oscar count?', 'a': '3', 'w': ['1', '5', '7']},
                    {'q': 'Keanu Reeves\' band name?', 'a': 'Dogstar', 'w': ['The Matrix', 'Speed', 'John Wick']},
                    {'q': 'Leonardo DiCaprio first Oscar?', 'a': 'The Revenant', 'w': ['Titanic', 'Wolf of Wall Street', 'Inception']},
                    {'q': 'Oprah Winfrey middle name?', 'a': 'Gail', 'w': ['Mary', 'Ann', 'Elizabeth']},
                    {'q': 'Lady Gaga real name?', 'a': 'Stefani', 'w': ['Angelina', 'Madonna', 'Joanne']},
                ]
            },
            'History': {
                'Easy': [
                    {'q': 'First US President?', 'a': 'George Washington', 'w': ['Lincoln', 'Adams', 'Jefferson']},
                    {'q': 'Who built the Pyramids?', 'a': 'Egyptians', 'w': ['Aztecs', 'Mayans', 'Romans']},
                    {'q': 'Year WW2 ended?', 'a': '1945', 'w': ['1944', '1946', '1918']},
                    {'q': 'Ship that sank in 1912?', 'a': 'Titanic', 'w': ['Lusitania', 'Bismarck', 'Olympic']},
                    {'q': 'First man on the Moon?', 'a': 'Neil Armstrong', 'w': ['Buzz Aldrin', 'Yuri Gagarin', 'Elon Musk']},
                ],
                'Medium': [
                    {'q': 'Year Berlin Wall fell?', 'a': '1989', 'w': ['1991', '1987', '1985']},
                    {'q': 'Who built the Colosseum?', 'a': 'Romans', 'w': ['Greeks', 'Ottomans', 'Persians']},
                    {'q': 'Treaty that ended WW1?', 'a': 'Versailles', 'w': ['Paris', 'Ghent', 'Berlin']},
                    {'q': 'Magna Carta signed in?', 'a': '1215', 'w': ['1066', '1348', '1492']},
                    {'q': 'Last Tsar of Russia?', 'a': 'Nicholas II', 'w': ['Alexander III', 'Peter I', 'Ivan IV']},
                ],
                'Hard': [
                    {'q': 'Byzantine Empire capital?', 'a': 'Constantinople', 'w': ['Rome', 'Athens', 'Alexandria']},
                    {'q': 'Code name for Normandy invasion?', 'a': 'Overlord', 'w': ['Barbarossa', 'Dynamo', 'Torch']},
                    {'q': 'Hundred Years\' War length?', 'a': '116 years', 'w': ['100 years', '99 years', '150 years']},
                    {'q': 'First woman Nobel Prize?', 'a': 'Marie Curie', 'w': ['Mother Teresa', 'Ada Lovelace', 'Rosa Parks']},
                    {'q': 'Battle of Waterloo year?', 'a': '1815', 'w': ['1805', '1812', '1820']},
                ]
            },
            'Geography': {
                'Easy': [
                    {'q': 'Largest continent?', 'a': 'Asia', 'w': ['Africa', 'Europe', 'North America']},
                    {'q': 'Capital of France?', 'a': 'Paris', 'w': ['Lyon', 'Nice', 'Marseille']},
                    {'q': 'Largest ocean?', 'a': 'Pacific', 'w': ['Atlantic', 'Indian', 'Arctic']},
                    {'q': 'Tallest mountain?', 'a': 'Everest', 'w': ['K2', 'Kilimanjaro', 'Mont Blanc']},
                    {'q': 'Country of Amazon forest?', 'a': 'Brazil', 'w': ['Australia', 'Egypt', 'China']},
                ],
                'Medium': [
                    {'q': 'Smallest country?', 'a': 'Vatican City', 'w': ['Monaco', 'Nauru', 'Malta']},
                    {'q': 'Capital of Australia?', 'a': 'Canberra', 'w': ['Sydney', 'Melbourne', 'Perth']},
                    {'q': 'Largest desert?', 'a': 'Sahara', 'w': ['Gobi', 'Kalahari', 'Arctic']},
                    {'q': 'River through Grand Canyon?', 'a': 'Colorado', 'w': ['Nile', 'Amazon', 'Mississippi']},
                    {'q': 'Country with most lakes?', 'a': 'Canada', 'w': ['Russia', 'USA', 'Finland']},
                ],
                'Hard': [
                    {'q': 'Sea with no coastline?', 'a': 'Sargasso Sea', 'w': ['Caspian Sea', 'Dead Sea', 'Yellow Sea']},
                    {'q': 'Deepest point in ocean?', 'a': 'Mariana Trench', 'w': ['Tonga', 'Java', 'Puerto Rico']},
                    {'q': 'Capital of Estonia?', 'a': 'Tallinn', 'w': ['Riga', 'Vilnius', 'Helsinki']},
                    {'q': 'Range between Europe/Asia?', 'a': 'Urals', 'w': ['Alps', 'Andes', 'Himalayas']},
                    {'q': 'Country with most islands?', 'a': 'Sweden', 'w': ['Indonesia', 'Philippines', 'Norway']},
                ]
            },
            'Politics': {
                'Easy': [
                    {'q': 'Head of UK government?', 'a': 'Prime Minister', 'w': ['King', 'President', 'Senator']},
                    {'q': 'US Congress houses?', 'a': '2', 'w': ['1', '3', '4']},
                    {'q': 'UN location?', 'a': 'New York', 'w': ['London', 'Paris', 'Geneva']},
                    {'q': 'System where people vote?', 'a': 'Democracy', 'w': ['Monarchy', 'Anarchy', 'Dictatorship']},
                    {'q': 'US President term (years)?', 'a': '4', 'w': ['2', '5', '6']},
                ],
                'Medium': [
                    {'q': 'US Senate seat count?', 'a': '100', 'w': ['50', '435', '200']},
                    {'q': 'Upper house of US?', 'a': 'Senate', 'w': ['House', 'Diet', 'Parliament']},
                    {'q': 'Age to be US President?', 'a': '35', 'w': ['25', '30', '40']},
                    {'q': 'UN Security Council permanents?', 'a': '5', 'w': ['10', '15', '3']},
                    {'q': 'First female UK PM?', 'a': 'Margaret Thatcher', 'w': ['Theresa May', 'Liz Truss', 'Queen Victoria']},
                ],
                'Hard': [
                    {'q': 'Magna Carta signing year?', 'a': '1215', 'w': ['1776', '1066', '1492']},
                    {'q': 'Apartheid country?', 'a': 'South Africa', 'w': ['USA', 'India', 'Brazil']},
                    {'q': 'EU headquarters city?', 'a': 'Brussels', 'w': ['Paris', 'Berlin', 'Strasbourg']},
                    {'q': 'US Vice President role in Senate?', 'a': 'President', 'w': ['Clerk', 'Whip', 'Leader']},
                    {'q': 'Cold War superpowers?', 'a': 'USA & USSR', 'w': ['UK & France', 'China & Japan', 'Germany & Italy']},
                ]
            },
            'Current Affairs': {
                'Easy': [
                    {'q': 'Currency of Japan?', 'a': 'Yen', 'w': ['Yuan', 'Won', 'Dollar']},
                    {'q': 'Tesla CEO?', 'a': 'Elon Musk', 'w': ['Jeff Bezos', 'Gates', 'Cook']},
                    {'q': 'Ukraine capital?', 'a': 'Kyiv', 'w': ['Lviv', 'Odessa', 'Moscow']},
                    {'q': 'Language of Brazil?', 'a': 'Portuguese', 'w': ['Spanish', 'French', 'English']},
                    {'q': 'Olympic host in 2024?', 'a': 'Paris', 'w': ['Tokyo', 'LA', 'London']},
                ],
                'Medium': [
                    {'q': 'G7 host 2024?', 'a': 'Italy', 'w': ['Japan', 'USA', 'Germany']},
                    {'q': 'World\'s most populous nation?', 'a': 'India', 'w': ['China', 'USA', 'Indonesia']},
                    {'q': 'BRICS new member 2024?', 'a': 'UAE', 'w': ['Japan', 'France', 'Canada']},
                    {'q': 'Nato newest member (2024)?', 'a': 'Sweden', 'w': ['Finland', 'Ukraine', 'Georgia']},
                    {'q': 'World\'s richest man (current)?', 'a': 'Elon Musk', 'w': ['Bezos', 'Arnault', 'Gates']},
                ],
                'Hard': [
                    {'q': '2024 COP29 host?', 'a': 'Azerbaijan', 'w': ['UAE', 'Brazil', 'Egypt']},
                    {'q': 'ICC headquarters?', 'a': 'The Hague', 'w': ['Geneva', 'Brussels', 'New York']},
                    {'q': 'European Central Bank location?', 'a': 'Frankfurt', 'w': ['Berlin', 'Paris', 'London']},
                    {'q': 'India G20 presidency year?', 'a': '2023', 'w': ['2024', '2022', '2025']},
                    {'q': 'Total countries in EU?', 'a': '27', 'w': ['28', '25', '30']},
                ]
            }
        }

        # Structure of the App
        structure = {
            'Academic': {'icon': 'bi-book', 'subs': ['Physics', 'Chemistry', 'Mathematics', 'Biology']},
            'Entertainment': {'icon': 'bi-controller', 'subs': ['Movies', 'Music', 'Gaming', 'Celebrities']},
            'General Knowledge': {'icon': 'bi-globe', 'subs': ['History', 'Geography', 'Politics', 'Current Affairs']}
        }

        # Main Seeding Loop
        for cat_name, info in structure.items():
            cat = Category.objects.create(name=cat_name, icon_class=info['icon'])
            for sub_name in info['subs']:
                sub = Subcategory.objects.create(category=cat, name=sub_name)
                
                for level in ['Easy', 'Medium', 'Hard']:
                    bank = data_bank.get(sub_name, {}).get(level, [])
                    
                    for item in bank:
                        q = Question.objects.create(
                            subcategory=sub, 
                            text=item['q'], 
                            difficulty=level
                        )
                        
                        # Create Choices (1 correct, 3 wrong)
                        choices = [Choice(question=q, text=item['a'], is_correct=True)]
                        for w_text in item['w']:
                            choices.append(Choice(question=q, text=w_text, is_correct=False))
                        
                        # Randomize display order
                        random.shuffle(choices)
                        Choice.objects.bulk_create(choices)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded 180 real questions!'))