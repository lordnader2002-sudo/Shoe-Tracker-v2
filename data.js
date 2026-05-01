// Sneaker release data — sourced from project repo, with synthetic enrichment
// (colorways, sale methods, market values) for prototype demonstration.
// Dates are anchored to "today" so the prototype always feels live.

(function () {
  const TODAY = new Date();
  TODAY.setHours(0, 0, 0, 0);

  function dayOffset(n) {
    const d = new Date(TODAY);
    d.setDate(d.getDate() + n);
    return d.toISOString().slice(0, 10);
  }

  // [name, brand, dayOffset, retail, hype_score, hype_level, colorway, style_code, sale_method, market_value]
  const RAW = [
    ["Nike GT Future “Unseen Hours”", "Nike", 0, 210, 4, "MEDIUM", "Black/Volt", "FZ4884-001", "SNKRS App", null],
    ["Dylan Harper x Nike GT Cut 1 “Unseen Hours”", "Nike", 0, 200, 4, "MEDIUM", "White/Crimson", "FZ4881-100", "SNKRS App", null],
    ["Nike Ja 3 “At Dawn”", "Nike", 0, 135, 4, "MEDIUM", "Pale Ivory/Coral", "HF8294-100", "Online + Retail", null],
    ["Fragment x Nike Mind 001", "Nike", 0, 90, 6, "MEDIUM", "Stone/Sail", "HM2210-200", "SNKRS App", 180],
    ["Fragment x Nike Mind 002", "Nike", 0, 140, 6, "MEDIUM", "Anthracite", "HM2211-001", "SNKRS App", 240],
    ["Nike Ja 3 “Tri-State”", "Nike", 0, 135, 4, "MEDIUM", "Royal/Orange", "HF8295-401", "Online + Retail", null],
    ["Nike GT Cut “Dylan Harper”", "Nike", 0, 200, 4, "MEDIUM", "Maroon/White", "FZ4882-600", "SNKRS App", null],
    ["Nike Book 2 “Must Be The Denim”", "Nike", 1, 145, 4, "MEDIUM", "Indigo/Cream", "HJ8821-401", "Online + Retail", null],
    ["Nike Zoom Hyperflight “Black”", "Nike", 1, 170, 4, "MEDIUM", "Triple Black", "FN6843-001", "Online + Retail", null],
    ["Nike KD 6 “Peanut Butter Jelly” 2026", "Nike", 1, 140, 5, "MEDIUM", "Wheat/Grape", "HM4422-200", "Online + Retail", 175],
    ["Air Jordan 14 “Black University Blue” 2026", "Jordan", 2, 215, 7, "HIGH", "Black/University Blue", "DR9580-041", "SNKRS App", 320],
    ["Pharrell adidas Adistar Jellyfish “Triple Black”", "Adidas", 2, 300, 5, "MEDIUM", "Triple Black", "JJ9921", "Confirmed App", null],
    ["Division St. x Nike Air Max 95 “Oregon Ducks” Pack", "Nike", 2, 250, 7, "HIGH", "Apple Green/Yellow", "HM3320-300", "Raffle/Dropship", 410],
    ["Swarovski x Air Jordan 1 High OG", "Jordan", 2, 1005, 9, "EXTREME", "Crystal/Black", "HM7711-001", "Raffle/Dropship", 2400],
    ["Avirex x adidas Superstar 82", "Adidas", 2, 180, 3, "LOW", "Cream/Brown Leather", "KJ3005", "Online + Retail", null],
    ["Kobe Bryant x Nike Air Force 1 Low “Lower Merion Aces Away”", "Nike", 4, 120, 7, "HIGH", "White/Maroon/Gold", "HF8112-100", "SNKRS App", 285],
    ["Nike Kobe 5 Protro “Lower Merion Aces Away” 2026", "Nike", 4, 200, 7, "HIGH", "White/Maroon/Gold", "HF8113-100", "SNKRS App", 360],
    ["Nike Kobe Dunk Low Protro “Lower Merion Aces”", "Nike", 4, 130, 7, "HIGH", "White/Maroon/Gold", "HF8114-100", "SNKRS App", 280],
    ["Nike LeBron 23 “Masked Menace”", "Nike", 5, 210, 7, "HIGH", "Black/Crimson/Silver", "HM7798-001", "Online + Retail", 290],
    ["Thug Club x adidas Adifom IIInfinity Mule", "Adidas", 6, 80, 3, "LOW", "Mocha", "JI8842", "Online + Retail", null],
    ["Thug Club x adidas Superstar Vintage", "Adidas", 6, 160, 3, "LOW", "Antique Cream", "JI8843", "Online + Retail", null],
    ["Thug Club x adidas AdiFom Megaride", "Adidas", 6, 170, 3, "LOW", "Bone/Brown", "JI8844", "Online + Retail", null],
    ["Nike Air Max 95 “Paisley Bandana”", "Nike", 7, 200, 7, "HIGH", "Bandana Blue/White", "HM2031-400", "Online + Retail", 295],
    ["Nike Air Max 90 “Infrared Reflective”", "Nike", 7, 150, 7, "HIGH", "White/Infrared/Black", "HM2032-100", "Online + Retail", 240],
    ["Nike Air Max 95 “Pink Foam” (W)", "Nike", 7, 190, 7, "HIGH", "Pink Foam/Sail", "HM2033-600", "Online + Retail", 270],
    ["Nike Air Liquid Max “Poison Dart Frog”", "Nike", 7, 230, 4, "MEDIUM", "Volt/Cobalt/Black", "HM2034-300", "Online + Retail", null],
    ["Nike Air Foamposite Pro “University Blue” 2026", "Nike", 8, 240, 7, "HIGH", "University Blue/Black", "624041-401", "SNKRS App", 380],
    ["Virgil Abloh Archive x Air Jordan 1 High OG “Alaska”", "Jordan", 9, 230, 9, "EXTREME", "White/Glacier Blue", "HM9921-100", "Raffle/Dropship", 1450],
    ["Air Jordan 3 “Spring is in the Air”", "Jordan", 9, 215, 7, "HIGH", "Sail/Pastel Pink", "HM9922-100", "SNKRS App", 320],
    ["Nike GT Future “Swooshman”", "Nike", 9, 190, 4, "MEDIUM", "Multi-color", "HM9923-900", "SNKRS App", null],
    ["NOTE Manchester x Nike SB Dunk Low “Brew & Biscuits”", "Nike", 9, 130, 7, "HIGH", "Tea Brown/Cream", "HM9924-200", "Raffle/Dropship", 410],
    ["adidas BadBo 1.0 “Rise”", "Adidas", 9, 160, 3, "LOW", "Solar/Black", "JJ4421", "Confirmed App", null],
    ["LEGO x Nike Air Max 95 (GS)", "Nike", 9, 162, 7, "HIGH", "Primary/Yellow/Red", "HM9925-700", "SNKRS App", 360],
    ["Nike GT Future “Galaxy Aura”", "Nike", 11, 210, 4, "MEDIUM", "Galaxy Multi", "HM9926-001", "SNKRS App", null],
    ["Jordan Jumpman Pro “Black Concord”", "Jordan", 12, 145, 5, "MEDIUM", "Black/Concord", "HM9927-001", "Online + Retail", null],
    ["Nike Sabrina 3 “What The”", "Nike", 13, 145, 4, "MEDIUM", "Multi-color", "HM9928-900", "Online + Retail", null],
    ["Nike Mind 001 “Geode Teal”", "Nike", 14, 95, 4, "MEDIUM", "Teal/Sail", "HM2210-301", "SNKRS App", null],
    ["Converse SHAI 001 “Camo”", "Converse", 15, 130, 3, "LOW", "Camo/Black", "A12345", "Online + Retail", null],
    ["Fragment x Nike Air Liquid Max", "Nike", 15, 225, 6, "MEDIUM", "Stone/Volt", "HM7811-200", "SNKRS App", 280],
    ["Nike LeBron 23 “Good Intentions”", "Nike", 15, 235, 7, "HIGH", "Pearl/Gold/Cream", "HM7812-100", "SNKRS App", 320],
    ["Air Jordan 3 “Orange Citrus” 2026", "Jordan", 16, 205, 7, "HIGH", "White/Citrus/Black", "HM9930-100", "SNKRS App", 290],
    ["Nike Ja 3 “Jurassic Park”", "Nike", 22, 135, 4, "MEDIUM", "Forest/Amber", "HM9931-300", "Online + Retail", null],
    ["Jurassic Park x Nike Ja 3 “Raptor”", "Nike", 22, 135, 4, "MEDIUM", "Olive/Black", "HM9932-200", "Online + Retail", null],
    ["Jurassic Park x Nike Ja 3 “Explorer”", "Nike", 22, 135, 4, "MEDIUM", "Khaki/Brown", "HM9933-200", "Online + Retail", null],
    ["Nike Air Max Uptempo 95 “Derek Fisher”", "Nike", 23, 170, 4, "MEDIUM", "Purple/Gold/White", "HM9934-500", "Online + Retail", null],
    ["Air Jordan 1 High OG “Flight Club”", "Jordan", 23, 185, 7, "HIGH", "White/Royal/Red", "HM9935-100", "SNKRS App", 280],
    ["adidas Anthony Edwards 2 “Lime Burst”", "Adidas", 24, 130, 3, "LOW", "Lime/Black", "JJ4422", "Online + Retail", null],
    ["Nike Kobe 11 Elite Protro “Mamba Out”", "Nike", 25, 220, 7, "HIGH", "Black/Gold/Maroon", "HM9936-001", "SNKRS App", 340],
    ["adidas Harden Vol. 10 “Lucid Aquamarine”", "Adidas", 28, 160, 3, "LOW", "Aquamarine/White", "JJ4423", "Confirmed App", null],
    ["Nike Air Foamposite Pro “Voltage”", "Nike", 29, 240, 7, "HIGH", "Volt/Black", "HM9937-700", "SNKRS App", 320],
    ["Nike Cryoshot Mercurial Vapor R9 “Varsity Royal”", "Nike", 30, 210, 4, "MEDIUM", "Royal/White", "HM9938-400", "Online + Retail", null],
    ["Nike Air Foamposite Pro “Green Camo” 2026", "Nike", 30, 240, 7, "HIGH", "Camo/Volt", "HM9939-300", "SNKRS App", 295],
    ["New Balance 1906R “Stone Pink”", "New Balance", 32, 160, 6, "MEDIUM", "Stone Pink/Cream", "M1906RPK", "Online + Retail", 210],
    ["Aimé Leon Dore x New Balance 990v6 “Olive”", "New Balance", 35, 220, 9, "EXTREME", "Olive/Cream", "M990AL6", "Raffle/Dropship", 1100],
    ["Travis Scott x Air Jordan 4 Low “Cactus Trail”", "Jordan", 38, 250, 10, "EXTREME", "Sand/Cactus/Black", "HM4444-200", "Raffle/Dropship", 1850],
    ["adidas Samba OG “Cloud White / Black”", "Adidas", 41, 100, 5, "MEDIUM", "White/Black/Gum", "B75806", "Online + Retail", 140],
    ["Nike Dunk Low “Panda” Restock", "Nike", 44, 115, 6, "MEDIUM", "White/Black", "DD1391-100", "Online + Retail", 165],
    ["Air Jordan 11 “Cherry” GS", "Jordan", 47, 150, 8, "HIGH", "White/Cherry/Black", "DZ4475-116", "SNKRS App", 290],
    ["HOKA Bondi 9 “Glacier”", "HOKA", 50, 170, 3, "LOW", "Glacier/Sail", "HK1009GL", "Online + Retail", null],
    ["On Cloudmonster 2 “Eclipse”", "On", 53, 180, 3, "LOW", "Eclipse/Magnet", "ON-CM2-EC", "Online + Retail", null],
    ["Yeezy Boost 350 V2 “Bone” Restock", "Yeezy", 56, 230, 8, "HIGH", "Bone/Cream", "HQ6316", "Confirmed App", 380],
    ["sacai x Nike Vaporwaffle “Lichen”", "Nike", 60, 180, 9, "EXTREME", "Lichen/Sail", "DD1875-300", "Raffle/Dropship", 720],
    ["Supreme x Nike Air Max 96 “Rust”", "Nike", 64, 190, 9, "EXTREME", "Rust/Black", "HM5566-600", "Raffle/Dropship", 840],
    ["Bad Bunny x adidas Gazelle “Chocolate”", "Adidas", 68, 160, 9, "EXTREME", "Cocoa/Cream", "JK4422", "Confirmed App", 620],
    ["New Balance 990v7 “Made in USA Grey”", "New Balance", 72, 220, 6, "MEDIUM", "Grey/Silver", "M990GR7", "Online + Retail", 280],
    ["Air Jordan 4 “White Cement” 2026", "Jordan", 76, 215, 8, "HIGH", "White/Black/Cement", "DH6927-100", "SNKRS App", 380],
  ];

  const SOURCES = [
    { name: "SneakerFiles", domain: "sneakerfiles.com" },
    { name: "NiceKicks", domain: "nicekicks.com" },
    { name: "Sneaker Bar Detroit", domain: "sneakerbardetroit.com" },
  ];

  window.RELEASES = RAW.map(([name, brand, days, price, score, level, colorway, style, method, mv], i) => {
    const src = SOURCES[i % SOURCES.length];
    const query = encodeURIComponent(`${name} ${style}`);
    return {
    id: "rel-" + i,
    name,
    brand,
    release_date: dayOffset(days),
    days_until_release: days,
    retail_price: price,
    estimated_market_value: mv,
    colorway,
    style_code: style,
    sale_method: method,
    hype_score: score,
    hype_level: level,
    source: src.name,
    source_url: `https://www.google.com/search?q=site%3A${src.domain}+${query}`,
  };
  });

  window.GENERATED_AT = new Date().toLocaleString("en-US", {
    month: "short", day: "numeric", year: "numeric",
    hour: "numeric", minute: "2-digit", hour12: true,
  });

  // Buy-at retailer logic. Sneaker drops sell through different channels;
  // we return real retailer search URLs scoped to the shoe's name + style code.
  window.buyLinks = function (r) {
    const q = encodeURIComponent(`${r.name} ${r.style_code}`);
    const links = [];
    const method = r.sale_method;
    const brand = r.brand;

    // Primary brand-app drop (early access)
    if (method === "SNKRS App") {
      links.push({ name: "Nike SNKRS", tag: "Primary · raffle entry", url: `https://www.nike.com/launch?s=${q}`, primary: true });
    } else if (method === "Confirmed App") {
      links.push({ name: "adidas Confirmed", tag: "Primary · raffle entry", url: `https://www.adidas.com/us/confirmed?q=${q}`, primary: true });
    } else if (brand === "Nike" || brand === "Jordan") {
      links.push({ name: "Nike.com", tag: "Brand · launch page", url: `https://www.nike.com/w?q=${q}`, primary: true });
    } else if (brand === "Adidas") {
      links.push({ name: "adidas.com", tag: "Brand · launch page", url: `https://www.adidas.com/us/search?q=${q}`, primary: true });
    } else if (brand === "New Balance") {
      links.push({ name: "newbalance.com", tag: "Brand · launch page", url: `https://www.newbalance.com/search?q=${q}`, primary: true });
    } else if (brand === "Converse") {
      links.push({ name: "converse.com", tag: "Brand · launch page", url: `https://www.converse.com/shop/search?q=${q}`, primary: true });
    }

    // Major retailers (always added)
    if (method === "Raffle/Dropship") {
      links.push({ name: "END.", tag: "Raffle entry", url: `https://www.endclothing.com/us/search?search=${q}` });
      links.push({ name: "Sneakersnstuff", tag: "Raffle entry", url: `https://www.sneakersnstuff.com/en/search?q=${q}` });
    }
    links.push({ name: "Foot Locker", tag: "Retailer", url: `https://www.footlocker.com/search?query=${q}` });
    links.push({ name: "Finish Line", tag: "Retailer", url: `https://www.finishline.com/store/search/searchResults.jsp?Ntt=${q}` });

    // Resell — always shown (in case missed retail)
    links.push({ name: "StockX", tag: "Resell market", url: `https://stockx.com/search?s=${q}`, resell: true });
    links.push({ name: "GOAT", tag: "Resell market", url: `https://www.goat.com/search?query=${q}`, resell: true });

    return links;
  };

  // Brand metadata for brand pages
  window.BRAND_META = {
    "Nike":        { tagline: "Beaverton, OR",      hue: 210, founded: 1964 },
    "Jordan":      { tagline: "Jumpman",            hue: 0,   founded: 1984 },
    "Adidas":      { tagline: "Herzogenaurach",     hue: 30,  founded: 1949 },
    "New Balance": { tagline: "Boston, MA",         hue: 250, founded: 1906 },
    "Yeezy":       { tagline: "Calabasas",          hue: 50,  founded: 2015 },
    "Converse":    { tagline: "All-Star",           hue: 0,   founded: 1908 },
    "HOKA":        { tagline: "Trail / Road",       hue: 160, founded: 2009 },
    "On":          { tagline: "Zürich",             hue: 180, founded: 2010 },
  };
})();
