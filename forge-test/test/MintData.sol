// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

struct MintEntry {
    uint256 tokenId;
    address user;
    uint256 mintAmount;
    uint256 depositAmount;
}

library MintData {
    uint256 internal constant COUNT = 880;

    function getEntries() internal pure returns (MintEntry[] memory) {
        MintEntry[] memory entries = new MintEntry[](880);

        entries[0] = MintEntry({
            tokenId: 1,
            user: 0x0009d32184AfC79797eC63589e62Ad5B53134AAd,
            mintAmount: 72517646650720701039,
            depositAmount: 169831698985335420000
        });
        entries[1] = MintEntry({
            tokenId: 2,
            user: 0x001098FEBF4e26D8d08E54655C0DCAB607072df4,
            mintAmount: 1017897025454211915607,
            depositAmount: 2395541729024922400000
        });
        entries[2] = MintEntry({
            tokenId: 5,
            user: 0x005b0743D8b2eD646499dC48b64B95E71B8afa43,
            mintAmount: 303232588856716596580,
            depositAmount: 1011915350658962200000
        });
        entries[3] = MintEntry({
            tokenId: 6,
            user: 0x00983187E18f62a2ac1dceBd63f2e5F50394cc74,
            mintAmount: 294488781766371551132,
            depositAmount: 720053990640000000000
        });
        entries[4] = MintEntry({
            tokenId: 7,
            user: 0x00f9da19ca19947815E3e88640538435c0946240,
            mintAmount: 4754689457796413868,
            depositAmount: 12560000000000000000
        });
        entries[5] = MintEntry({
            tokenId: 9,
            user: 0x012b41FBbebB18628DD430f6DfABF94F9E8160DD,
            mintAmount: 9129539208785887443,
            depositAmount: 25706392029748670000
        });
        entries[6] = MintEntry({
            tokenId: 10,
            user: 0x012E168ACb9fdc90a4ED9fd6cA2834D9bF5b579e,
            mintAmount: 574279977333361417827,
            depositAmount: 1380615646446726000000
        });
        entries[7] = MintEntry({
            tokenId: 12,
            user: 0x01b9369cf8624E1f9960864c18411B4b07Eb91AC,
            mintAmount: 854813567554448994796,
            depositAmount: 2742339227726096400000
        });
        entries[8] = MintEntry({
            tokenId: 13,
            user: 0x021028695EAfDDe60E139D87000a8bd6cB65645e,
            mintAmount: 73804819574994541642,
            depositAmount: 190260000000000000000
        });
        entries[9] = MintEntry({
            tokenId: 14,
            user: 0x0212fBfB3bbA5d8566F09E8Ef78BCde68CCB30A3,
            mintAmount: 763688019202854213174,
            depositAmount: 1952083797684760000000
        });
        entries[10] = MintEntry({
            tokenId: 15,
            user: 0x02131F806a105353D9c7A13900c6a510b59DF80b,
            mintAmount: 12675807481807014130,
            depositAmount: 50060194472465190000
        });
        entries[11] = MintEntry({
            tokenId: 18,
            user: 0x027f7432906e21F381197124397a4d27ff709BB7,
            mintAmount: 4447613024872764212989,
            depositAmount: 14100000000000000000000
        });
        entries[12] = MintEntry({
            tokenId: 19,
            user: 0x02Ca2568cFd5014566352022d126472B21279EdB,
            mintAmount: 629057502396680342282,
            depositAmount: 1504555436301765600000
        });
        entries[13] = MintEntry({
            tokenId: 20,
            user: 0x02Cdb392a6D69e5c2a970baA9B40EcE990715E1D,
            mintAmount: 45674698667818615301,
            depositAmount: 149999930322905000000
        });
        entries[14] = MintEntry({
            tokenId: 23,
            user: 0x032c701886AD0317F0E58C8F4a570c6F9C0BBf4a,
            mintAmount: 54785391822967001362,
            depositAmount: 149230969200289480000
        });
        entries[15] = MintEntry({
            tokenId: 24,
            user: 0x035Fc3B0ec2487c1c9dEF561F578ec77a06B1b12,
            mintAmount: 3959906883807915234175,
            depositAmount: 11623910833993550000000
        });
        entries[16] = MintEntry({
            tokenId: 26,
            user: 0x042d7f399342B14166E5C716b816cBC1fc649511,
            mintAmount: 2660540569292868935,
            depositAmount: 10000000000000000000
        });
        entries[17] = MintEntry({
            tokenId: 27,
            user: 0x04a8F225d9057c468B5062C668Dcd7DB725aC321,
            mintAmount: 427647439848464348813,
            depositAmount: 1013644119729029600000
        });
        entries[18] = MintEntry({
            tokenId: 28,
            user: 0x04F4320a12DdB86Ca115E43C77B2155459244942,
            mintAmount: 33189371676801337358,
            depositAmount: 95164426520000000000
        });
        entries[19] = MintEntry({
            tokenId: 29,
            user: 0x050b0Fe971B95dA31E34ea2EFC417aD187e76Fb8,
            mintAmount: 36617359379870322703,
            depositAmount: 92778563931882640000
        });
        entries[20] = MintEntry({
            tokenId: 30,
            user: 0x062164d0C571002b9b34a9a71dDAEeb0b6f93132,
            mintAmount: 658030107269400706833,
            depositAmount: 1814095111241686800000
        });
        entries[21] = MintEntry({
            tokenId: 31,
            user: 0x06850a5c42D8F51c5B10aA573A9569B75e1666a7,
            mintAmount: 1341036911724537024695,
            depositAmount: 3913972782420000000000
        });
        entries[22] = MintEntry({
            tokenId: 32,
            user: 0x0691E1F7c2f6eDf28fBCCBa8844845ae5f53901E,
            mintAmount: 15334978488673001243,
            depositAmount: 40000000000000000000
        });
        entries[23] = MintEntry({
            tokenId: 36,
            user: 0x07a90e1b2788a108AAc075a8c987C9aa521497E6,
            mintAmount: 460164518915060317203,
            depositAmount: 1234767066057338500000
        });
        entries[24] = MintEntry({
            tokenId: 38,
            user: 0x07FC63Bb1Bfb664B1fcB41D8193738cad1255c09,
            mintAmount: 3270482939638034822964,
            depositAmount: 7682251006730489000000
        });
        entries[25] = MintEntry({
            tokenId: 39,
            user: 0x0822b01Ce57D3626D86774705dD772790e7CC470,
            mintAmount: 131356925116570565807,
            depositAmount: 309926044750000000000
        });
        entries[26] = MintEntry({
            tokenId: 40,
            user: 0x083203F1d4dbaB71e23b6B0298df2A7185440F46,
            mintAmount: 31146803416769879862801,
            depositAmount: 63313302465732720000000
        });
        entries[27] = MintEntry({
            tokenId: 41,
            user: 0x083BdBAA68acD8cBFDbE5502ea8a27e9322E9baE,
            mintAmount: 585928396852719458857,
            depositAmount: 1410422608843377500000
        });
        entries[28] = MintEntry({
            tokenId: 43,
            user: 0x087E8708F3c370f7f547cfD750939C17F301f5C3,
            mintAmount: 1501253111230260584970,
            depositAmount: 3494250000000000000000
        });
        entries[29] = MintEntry({
            tokenId: 44,
            user: 0x08AceA65474E0b290fe3D2598f8E78CAa352B570,
            mintAmount: 116608037158284042149,
            depositAmount: 278156550000000000000
        });
        entries[30] = MintEntry({
            tokenId: 45,
            user: 0x08FC2d49ac735e8fB5BF247ebd677f63DDfcBee4,
            mintAmount: 1756758711669950366,
            depositAmount: 5000000000000000000
        });
        entries[31] = MintEntry({
            tokenId: 46,
            user: 0x0929EC1f6257A5df91A2b7c7AF1292b0bBCE9B02,
            mintAmount: 8797098955267015643,
            depositAmount: 21748051095443608000
        });
        entries[32] = MintEntry({
            tokenId: 47,
            user: 0x094E715a19a7751f8c9b0D24A89B8Cc743Ad4E14,
            mintAmount: 35576519603464559309,
            depositAmount: 100541594767021420000
        });
        entries[33] = MintEntry({
            tokenId: 48,
            user: 0x09641015fB8b08388A7367b946e634d37DDdfFaa,
            mintAmount: 3335907507463834961,
            depositAmount: 9080731028482484000
        });
        entries[34] = MintEntry({
            tokenId: 49,
            user: 0x0979b13D93a61562Cea2149264cE709D05c82b55,
            mintAmount: 384518156496386340378,
            depositAmount: 893954545314412200000
        });
        entries[35] = MintEntry({
            tokenId: 50,
            user: 0x09C6232D54b51841A202D76F76Fa679df53a3B3e,
            mintAmount: 824404462697065812104,
            depositAmount: 2000000000000000000000
        });
        entries[36] = MintEntry({
            tokenId: 51,
            user: 0x0a8774781cBA956b6065840C2F09708832C541A9,
            mintAmount: 20417623624628002512,
            depositAmount: 49421990093769970000
        });
        entries[37] = MintEntry({
            tokenId: 52,
            user: 0x0aa8AFdc36571f9a37F3b9FEf0dfcACA66eA86D6,
            mintAmount: 875349011285371014565,
            depositAmount: 2335699793446397300000
        });
        entries[38] = MintEntry({
            tokenId: 53,
            user: 0x0b0806EE651e7B05fc383d1B1beD3525148E9E87,
            mintAmount: 6282525786974950971,
            depositAmount: 15000000000000000000
        });
        entries[39] = MintEntry({
            tokenId: 54,
            user: 0x0B2CA90dF1f1519A25da0fdDA1314A12e2092F34,
            mintAmount: 935168699855494021444,
            depositAmount: 2970695600000000000000
        });
        entries[40] = MintEntry({
            tokenId: 55,
            user: 0x0C4e11942715Bd67afA0A77329d7acb3b89f0418,
            mintAmount: 425286677431032138522,
            depositAmount: 1017722847129132300000
        });
        entries[41] = MintEntry({
            tokenId: 56,
            user: 0x0C6689245D23c2b1D51D5FEC17c4A5A00D83b372,
            mintAmount: 1595865891234032004523,
            depositAmount: 6457404183311591000000
        });
        entries[42] = MintEntry({
            tokenId: 57,
            user: 0x0C94eDF79a015337d0a3DeFe243Ba0C5b6ad1aAf,
            mintAmount: 85835398352315040757,
            depositAmount: 204451650656754500000
        });
        entries[43] = MintEntry({
            tokenId: 58,
            user: 0x0Cbb86FA9CFBf2B17CD9ae5022efE9DDD578051c,
            mintAmount: 2146729061326324081353,
            depositAmount: 6495122658785008000000
        });
        entries[44] = MintEntry({
            tokenId: 59,
            user: 0x0Cccd195c06Dd53e7e95f9dd68115d5de0be6B44,
            mintAmount: 74769098387161738597,
            depositAmount: 189119360000000000000
        });
        entries[45] = MintEntry({
            tokenId: 60,
            user: 0x0d07E592BaCA62Cfa18F692254158006934792D5,
            mintAmount: 75313977193148592007,
            depositAmount: 185000000000000000000
        });
        entries[46] = MintEntry({
            tokenId: 61,
            user: 0x0D39023c538a3B00b406E50768D4c9D2a59C15C2,
            mintAmount: 7499039626845026742,
            depositAmount: 20000000000000000000
        });
        entries[47] = MintEntry({
            tokenId: 62,
            user: 0x0d567E8BFE01D9a0E8F1F696ba0Deeb37f045211,
            mintAmount: 11664148283565677402,
            depositAmount: 28000000007934070000
        });
        entries[48] = MintEntry({
            tokenId: 63,
            user: 0x0DF190A2fb14DeB4ae241Fd280C5820A7259E1Ee,
            mintAmount: 4444405810856523758,
            depositAmount: 10640000000000000000
        });
        entries[49] = MintEntry({
            tokenId: 65,
            user: 0x0e44Ccebe5c4b5463291882d04c5a4Af1C2C04Be,
            mintAmount: 56565702795960451109,
            depositAmount: 135773575500000000000
        });
        entries[50] = MintEntry({
            tokenId: 67,
            user: 0x0edc16b7e2F36f3f3A6f523c6248181eF38fD715,
            mintAmount: 45862549700040560606,
            depositAmount: 109934550000000000000
        });
        entries[51] = MintEntry({
            tokenId: 68,
            user: 0x0Ee6Ff7a9FAb79952b4179654b97C7BAC82386c8,
            mintAmount: 408263367069769325713,
            depositAmount: 978289596440000000000
        });
        entries[52] = MintEntry({
            tokenId: 69,
            user: 0xbc1f278341c2DeDBBA9f3d98406d24DA09C8bD29,
            mintAmount: 3760626578747303326246,
            depositAmount: 7999955635739748000000
        });
        entries[53] = MintEntry({
            tokenId: 70,
            user: 0x0f7997042252Aae0F6F106298dC38F068f49a4eA,
            mintAmount: 39786080682969543524,
            depositAmount: 103778641000000000000
        });
        entries[54] = MintEntry({
            tokenId: 71,
            user: 0x0F96997c6Cbe8FB6DdADF2747A26614E3F7BAA57,
            mintAmount: 41948991895258640705,
            depositAmount: 100000000000000000000
        });
        entries[55] = MintEntry({
            tokenId: 74,
            user: 0x0FEEE57b985476A795DF5fFDA50f17Ed60D92873,
            mintAmount: 41948991895258640705,
            depositAmount: 100000000000000000000
        });
        entries[56] = MintEntry({
            tokenId: 75,
            user: 0x10485Fe2F23aFaa8a85Eef091b7233a600463c52,
            mintAmount: 62382310890820796261,
            depositAmount: 129166767667885330000
        });
        entries[57] = MintEntry({
            tokenId: 77,
            user: 0x10c9ccA806ba4A8f580fFedEcd9c2e8a49E6EF91,
            mintAmount: 2940436413770491732145,
            depositAmount: 7037928678205643000000
        });
        entries[58] = MintEntry({
            tokenId: 78,
            user: 0x110724F68a1aabaEd919810114Df0d3Db50Ab605,
            mintAmount: 326657708119067103331,
            depositAmount: 698741000000000000000
        });
        entries[59] = MintEntry({
            tokenId: 79,
            user: 0x1109940470391b15c0ecfC07B9f092B16CF36Ec6,
            mintAmount: 22778499541170048425,
            depositAmount: 61579690912646080000
        });
        entries[60] = MintEntry({
            tokenId: 80,
            user: 0x11153b62caC9A11f1D5CF6548dB69827139d25F9,
            mintAmount: 205930804566432451053,
            depositAmount: 473000000000000000000
        });
        entries[61] = MintEntry({
            tokenId: 81,
            user: 0x11360C928657afE5Cd536a4Cebf03Dee47bB2F4c,
            mintAmount: 42148716127547710006,
            depositAmount: 100000000000000000000
        });
        entries[62] = MintEntry({
            tokenId: 86,
            user: 0x1244d96845D94B3d1A550110A5C97Ef018F4d24E,
            mintAmount: 578734034438358530990,
            depositAmount: 1398955914020269300000
        });
        entries[63] = MintEntry({
            tokenId: 89,
            user: 0x12bB0AeA5c4bED1e050E4358D15e6c82BeB90d7b,
            mintAmount: 11928355791417993952,
            depositAmount: 27270086984676577000
        });
        entries[64] = MintEntry({
            tokenId: 90,
            user: 0x12d2dd1c6389A66a53f9AF8f1bb54607C6Ca1305,
            mintAmount: 20590083299462669867043,
            depositAmount: 59500000000000000000000
        });
        entries[65] = MintEntry({
            tokenId: 91,
            user: 0x131E1961b5Bd82a40B9EE9C4B1cbD0C0DF399342,
            mintAmount: 5959784462336318396459,
            depositAmount: 12233007255057783000000
        });
        entries[66] = MintEntry({
            tokenId: 92,
            user: 0x1436531126FC43B958F6C637F63C1186a8f07A93,
            mintAmount: 71955639557046675330,
            depositAmount: 286407763223514700000
        });
        entries[67] = MintEntry({
            tokenId: 93,
            user: 0x145c584F2F022997a9d0e5FcB4346042229525E1,
            mintAmount: 4601609723374720747908,
            depositAmount: 10148232856339088000000
        });
        entries[68] = MintEntry({
            tokenId: 94,
            user: 0x158523C18810737365EbF3DaAe3a80F9575bBCB5,
            mintAmount: 4645763100667419868902,
            depositAmount: 14604047074381957000000
        });
        entries[69] = MintEntry({
            tokenId: 95,
            user: 0x15962221e0E7A41dE9Da1615f9cb64cBfFF83408,
            mintAmount: 649829664129189922723,
            depositAmount: 1476345274319228000000
        });
        entries[70] = MintEntry({
            tokenId: 97,
            user: 0x169CbceaCaDc1d436D462A4Ca7836c5DD7fAEA43,
            mintAmount: 1827233210279026908990,
            depositAmount: 4500000000000000000000
        });
        entries[71] = MintEntry({
            tokenId: 98,
            user: 0x16Bd8953729774C820D8cC2C9caF7Ae332b5fB65,
            mintAmount: 91971191001981864673,
            depositAmount: 242951336620000000000
        });
        entries[72] = MintEntry({
            tokenId: 99,
            user: 0x16e13d9f28E2C3aceD2dd3cb383e0b68fd7a3c56,
            mintAmount: 120128567907123178719,
            depositAmount: 300000000000000000000
        });
        entries[73] = MintEntry({
            tokenId: 101,
            user: 0x177a981A8a9D0104e675F0c1EB2a1cF330bC5bCb,
            mintAmount: 2869572081045311943483,
            depositAmount: 6481108989688613000000
        });
        entries[74] = MintEntry({
            tokenId: 105,
            user: 0x1898fEa3b23f01EaBEF161603da4aB9003cbD732,
            mintAmount: 2457701153677742053097,
            depositAmount: 5477112412098487000000
        });
        entries[75] = MintEntry({
            tokenId: 106,
            user: 0x18bfE139224078667a714dFF35A9a04F30612310,
            mintAmount: 902832435751393633457,
            depositAmount: 2545960419677515500000
        });
        entries[76] = MintEntry({
            tokenId: 107,
            user: 0x18Df3818E91e7704b77493187bB4A3466AaFD5DD,
            mintAmount: 11847184570133415006,
            depositAmount: 100000000000000000000
        });
        entries[77] = MintEntry({
            tokenId: 108,
            user: 0x191635E87AaB411193B3BB89C27Cf707a716EF47,
            mintAmount: 7010791535089004886,
            depositAmount: 43658166506494870000
        });
        entries[78] = MintEntry({
            tokenId: 110,
            user: 0x195373B6ac3dFEB89D1657b8cbc2aE784F2AdbD3,
            mintAmount: 41779083015565532149,
            depositAmount: 99882000000000000000
        });
        entries[79] = MintEntry({
            tokenId: 113,
            user: 0x19ee961B247A33f8c5a4fCf1d10B7BD5F6D59F95,
            mintAmount: 136561715735316591871,
            depositAmount: 341160296160992500000
        });
        entries[80] = MintEntry({
            tokenId: 114,
            user: 0x1A625B318BEE661D175ECaf2130553eda32e37dd,
            mintAmount: 296488640162824814418,
            depositAmount: 978392666050000000000
        });
        entries[81] = MintEntry({
            tokenId: 115,
            user: 0x1a96f3Bc6cD0E9Db43E89f983d4227eC5F707539,
            mintAmount: 403137115408937505714,
            depositAmount: 1516950192761695600000
        });
        entries[82] = MintEntry({
            tokenId: 116,
            user: 0x1A979E39a5Cd60dE54E2CA4E1442c3AB7E636Ce3,
            mintAmount: 374218202053818020459,
            depositAmount: 1000000000000000000000
        });
        entries[83] = MintEntry({
            tokenId: 117,
            user: 0x1B3FE9546194739e58D887b7032cAb872B681203,
            mintAmount: 98211656617307069002,
            depositAmount: 242817039576143500000
        });
        entries[84] = MintEntry({
            tokenId: 118,
            user: 0x1b6aA23A4de4cF66303386de2DFcdAe29c7a43DA,
            mintAmount: 13990031586331600621,
            depositAmount: 32103065059812205000
        });
        entries[85] = MintEntry({
            tokenId: 119,
            user: 0x1Bd10F3ACeD07B3a99f3516b9b1Ed11ac26D638F,
            mintAmount: 182876554177805742821,
            depositAmount: 497674367679832100000
        });
        entries[86] = MintEntry({
            tokenId: 121,
            user: 0x1C31A5774bfa46Dea7C47AbE13CeE28680a40BEA,
            mintAmount: 8561665986034125944942,
            depositAmount: 25000000000000000000000
        });
        entries[87] = MintEntry({
            tokenId: 123,
            user: 0x1C8F9284F2C806D6e3A8D6Adcd49D5b3053Ff2DD,
            mintAmount: 56149813675391278132,
            depositAmount: 142450310110000000000
        });
        entries[88] = MintEntry({
            tokenId: 124,
            user: 0x1c9283aee32fA4FB74B5D0eEb84c55591E9b5Cb9,
            mintAmount: 35263084122650653816,
            depositAmount: 300000000000000000000
        });
        entries[89] = MintEntry({
            tokenId: 125,
            user: 0x1CB590691dc6500a039863d62dB3F8D6ca99775D,
            mintAmount: 1840018655025275079359,
            depositAmount: 5400524026163895000000
        });
        entries[90] = MintEntry({
            tokenId: 126,
            user: 0x1d0c5AE813FdA46D1BA0f18C9255C3390b1b6974,
            mintAmount: 35057943828411102953,
            depositAmount: 837941118638042300000
        });
        entries[91] = MintEntry({
            tokenId: 128,
            user: 0x1d840c4DdE769cA6d65Ab55398d1F60277f1963D,
            mintAmount: 80051716075388922352,
            depositAmount: 193932784071956200000
        });
        entries[92] = MintEntry({
            tokenId: 129,
            user: 0x1d8B7d3b3DEf5C8a4Df9f41c159F9b5b92Be70c4,
            mintAmount: 10948991895259640706,
            depositAmount: 100000000000000000000
        });
        entries[93] = MintEntry({
            tokenId: 131,
            user: 0x1db66aD6B4Ae6f850C8323605880E4F7895834D5,
            mintAmount: 40206247413297349656,
            depositAmount: 89678802500000000000
        });
        entries[94] = MintEntry({
            tokenId: 133,
            user: 0x1e33E838f51DaaCd9544BFc81bC6D175D23cFF47,
            mintAmount: 48740601969145823245,
            depositAmount: 122766810000000000000
        });
        entries[95] = MintEntry({
            tokenId: 134,
            user: 0x1e34B2316Fe3C50C2Cf345232263D1a897F9b104,
            mintAmount: 7373573918843122458,
            depositAmount: 20073478115691524000
        });
        entries[96] = MintEntry({
            tokenId: 135,
            user: 0x1E3A64ce9b4a573674284ab590b4Fc538746FA21,
            mintAmount: 206419167584579035460,
            depositAmount: 512530933340000000000
        });
        entries[97] = MintEntry({
            tokenId: 136,
            user: 0x1eB3b991e98C8C0F23402b9Bff90FE3DD20Bf1B4,
            mintAmount: 348838756318241141633,
            depositAmount: 1000231053370000000000
        });
        entries[98] = MintEntry({
            tokenId: 138,
            user: 0x1EEdEFf5Ce466e6687B18686c40ED0A34fEbd386,
            mintAmount: 41656694557394382531,
            depositAmount: 101498278776785880000
        });
        entries[99] = MintEntry({
            tokenId: 139,
            user: 0x1eFbF6e58192836025FB81CBA879704b2d78D1f2,
            mintAmount: 19217118176178424821255,
            depositAmount: 58170345945778230000000
        });
        entries[100] = MintEntry({
            tokenId: 140,
            user: 0x1Efc68d4513138F59DAA8316087709C5dEd0c91A,
            mintAmount: 15291235863602599007,
            depositAmount: 36422250876769698000
        });
        entries[101] = MintEntry({
            tokenId: 141,
            user: 0x1F2091d9D5D79D0B0d4752CD458c08920E80e814,
            mintAmount: 27549927369712392806,
            depositAmount: 74953871505754690000
        });
        entries[102] = MintEntry({
            tokenId: 142,
            user: 0x1f55e00f62d70bB00c0dba35B288d938085eC076,
            mintAmount: 159598681143550859400,
            depositAmount: 392873456000000000000
        });
        entries[103] = MintEntry({
            tokenId: 143,
            user: 0x1FE9Fd1156688699F4ca017E72ee0D9873f9d758,
            mintAmount: 73694369140265830010,
            depositAmount: 200000000000000000000
        });
        entries[104] = MintEntry({
            tokenId: 144,
            user: 0x1fF034901dbEe276aF5f75DbA762C3aeB59784D8,
            mintAmount: 1076748045234972439894,
            depositAmount: 2604105852938912500000
        });
        entries[105] = MintEntry({
            tokenId: 145,
            user: 0x1Ff37F8fE8c9adE1854822d48d33416F880Ff242,
            mintAmount: 417613241655584735169,
            depositAmount: 998752806000000000000
        });
        entries[106] = MintEntry({
            tokenId: 147,
            user: 0x206a077970AA30BD74542D6F7533E9F1adcf2839,
            mintAmount: 20820872340404450919,
            depositAmount: 50658592869756125000
        });
        entries[107] = MintEntry({
            tokenId: 148,
            user: 0x206F83ec8A1D66F0903a13E9Caf49aA5DF85C27b,
            mintAmount: 76387981776183606990,
            depositAmount: 193945117717200000000
        });
        entries[108] = MintEntry({
            tokenId: 149,
            user: 0x208437fF6D54fC97320D67f8BFE667EEbA5Df2e1,
            mintAmount: 63667846233229689726,
            depositAmount: 148813978876609200000
        });
        entries[109] = MintEntry({
            tokenId: 150,
            user: 0x21199C6C8B99553859258f921a7618Df70ef53D9,
            mintAmount: 110831123353403048644,
            depositAmount: 375000000000000000000
        });
        entries[110] = MintEntry({
            tokenId: 154,
            user: 0x21d35174385903A4f7887cc05592DbB02aFE528d,
            mintAmount: 39728645186229337141,
            depositAmount: 121879000289215680000
        });
        entries[111] = MintEntry({
            tokenId: 155,
            user: 0x2241ce35734fF196A6daC1180dE4a9261f874701,
            mintAmount: 89765050667951230420177,
            depositAmount: 299994343740000000000000
        });
        entries[112] = MintEntry({
            tokenId: 156,
            user: 0x225E9B54F41F44F42150b6aAA730Da5f2d23FAf2,
            mintAmount: 6749662195167790056151,
            depositAmount: 20000000000000000000000
        });
        entries[113] = MintEntry({
            tokenId: 159,
            user: 0x230AEf6528AC4A89DCE940D1959996eAa43f40C4,
            mintAmount: 37759715017271655406,
            depositAmount: 100000000000000000000
        });
        entries[114] = MintEntry({
            tokenId: 160,
            user: 0x23118DB7a1557cDF869C08c9E3D06D231893b16a,
            mintAmount: 33411463885464488839,
            depositAmount: 79078986377571100000
        });
        entries[115] = MintEntry({
            tokenId: 161,
            user: 0x2330eB2d92167c3b6B22690c03b508E0CA532980,
            mintAmount: 2355633261502803038427,
            depositAmount: 4808079337569121000000
        });
        entries[116] = MintEntry({
            tokenId: 162,
            user: 0x2333d701Ab84E0AFa6150a6708C16b71A6aFFE7E,
            mintAmount: 2353936980020216635602,
            depositAmount: 17790057512561543000000
        });
        entries[117] = MintEntry({
            tokenId: 163,
            user: 0x23531F1Cf89b73d0097165b62d028b269559dc47,
            mintAmount: 5194659861249948923,
            depositAmount: 11597243197903876000
        });
        entries[118] = MintEntry({
            tokenId: 164,
            user: 0x2362EF2344E71434F10B6b592232F4caaD15bB30,
            mintAmount: 226796384794071641250,
            depositAmount: 837726660480604700000
        });
        entries[119] = MintEntry({
            tokenId: 167,
            user: 0x242f0b090d2a5A7516f091d3dB051b22D45508b4,
            mintAmount: 8109510100193537080,
            depositAmount: 17587847090819858000
        });
        entries[120] = MintEntry({
            tokenId: 168,
            user: 0x243cdFDf30171Bd4959e9183a6F29f8EBa2559f6,
            mintAmount: 69128741032853537111,
            depositAmount: 165647799000000000000
        });
        entries[121] = MintEntry({
            tokenId: 169,
            user: 0x245059CA13382Af524b1c3a7374B8DC48a0f2195,
            mintAmount: 2956571105643780038291,
            depositAmount: 10000000000000000000000
        });
        entries[122] = MintEntry({
            tokenId: 170,
            user: 0x24a2D577B6141d6E0A7Adb8044FDD5365bd22170,
            mintAmount: 516777151325322337517,
            depositAmount: 1149571893179929200000
        });
        entries[123] = MintEntry({
            tokenId: 171,
            user: 0x24f8B34b3A381cc72576a35d55A6996c9bF2C4CB,
            mintAmount: 1498593991917486645828,
            depositAmount: 4000000000000000000000
        });
        entries[124] = MintEntry({
            tokenId: 173,
            user: 0x257075Aa0C4B06D7d59Def1f2848972BfaEa9aCE,
            mintAmount: 1370785558376091096777,
            depositAmount: 3246051721242411000000
        });
        entries[125] = MintEntry({
            tokenId: 174,
            user: 0x2606227f1Eb06106d7CeDCC10D927A9A91f3B6c2,
            mintAmount: 214744077534830212452,
            depositAmount: 514976280460379600000
        });
        entries[126] = MintEntry({
            tokenId: 175,
            user: 0x2642E2883BC7344a42334624AC7c9d9254E03D37,
            mintAmount: 2556077506199720777749,
            depositAmount: 7424699822779962000000
        });
        entries[127] = MintEntry({
            tokenId: 176,
            user: 0x269eACD11961EF75d3e54cE959A8c78aB6c994Ce,
            mintAmount: 691484331117472818263,
            depositAmount: 2885149659090000000000
        });
        entries[128] = MintEntry({
            tokenId: 177,
            user: 0x26c76F9893a74ec994E204cbaD68d2e3d8fad92F,
            mintAmount: 55802480247456241652,
            depositAmount: 230000000000000000000
        });
        entries[129] = MintEntry({
            tokenId: 178,
            user: 0x26dc3f258767b34Cf213a60A1b2E7D1F008Cfb48,
            mintAmount: 10350330979274899169064,
            depositAmount: 32589974692500000000000
        });
        entries[130] = MintEntry({
            tokenId: 179,
            user: 0x2702823b91733BB773b1E10256B32a576fe2ABA0,
            mintAmount: 111765837434816829522,
            depositAmount: 487000000000000000000
        });
        entries[131] = MintEntry({
            tokenId: 180,
            user: 0x278b99f8F14c1113371d5b2696C5BC5dd8B17fe4,
            mintAmount: 29369808622184300548,
            depositAmount: 62852782874342160000
        });
        entries[132] = MintEntry({
            tokenId: 181,
            user: 0x2790789939226Bf96f6CF7C2F4DD4C831a928D17,
            mintAmount: 1975107019386153888717,
            depositAmount: 4975340196478000000000
        });
        entries[133] = MintEntry({
            tokenId: 182,
            user: 0x27A28F390063C17C80186ED66d80d32fB11133Fa,
            mintAmount: 820067598645914766091,
            depositAmount: 2000000000000000000000
        });
        entries[134] = MintEntry({
            tokenId: 183,
            user: 0x27c72e4BD23C910218d8f06C4a1742E06657c874,
            mintAmount: 736467594012595974526,
            depositAmount: 2004751066226175200000
        });
        entries[135] = MintEntry({
            tokenId: 184,
            user: 0x28395ad01cA521Ec9f51b3a493b94E5104A276ea,
            mintAmount: 2384441287173651306859,
            depositAmount: 6900000000000000000000
        });
        entries[136] = MintEntry({
            tokenId: 185,
            user: 0x288074773717CE071B7aA306e94101cf0E4681A8,
            mintAmount: 73895146021881509614,
            depositAmount: 199670586100000000000
        });
        entries[137] = MintEntry({
            tokenId: 186,
            user: 0x28ac178f9B6B5746491099B04492730318f7D459,
            mintAmount: 110201936210033571716,
            depositAmount: 263617047400000000000
        });
        entries[138] = MintEntry({
            tokenId: 187,
            user: 0x28bf93AdD6daF977443d76681acF2AAbFeb1778f,
            mintAmount: 35898046323466098063,
            depositAmount: 93920000000000000000
        });
        entries[139] = MintEntry({
            tokenId: 189,
            user: 0x2949CaC4DFc9138e5Df3FCe87BB52A124614e959,
            mintAmount: 40328223247874693430,
            depositAmount: 96964410000000000000
        });
        entries[140] = MintEntry({
            tokenId: 190,
            user: 0x294ca11a4faEeB79Ff01E515d130772559f886EB,
            mintAmount: 136343920384768430798481,
            depositAmount: 276314976809117050000000
        });
        entries[141] = MintEntry({
            tokenId: 191,
            user: 0x29687E2a2b38bbc1f4f9069f1f24F13a3c83d27D,
            mintAmount: 26605913106267805759,
            depositAmount: 63551297243830410000
        });
        entries[142] = MintEntry({
            tokenId: 192,
            user: 0x29D2e1B1cB9D50824a24EDb7ea75C8d91931F415,
            mintAmount: 4183653309454125899924,
            depositAmount: 12203390004000000000000
        });
        entries[143] = MintEntry({
            tokenId: 194,
            user: 0x2a2b7015C8B308aa45cB4D6A5fEE46770d92Ce1A,
            mintAmount: 5529603894459766195207,
            depositAmount: 11788380244100000000000
        });
        entries[144] = MintEntry({
            tokenId: 195,
            user: 0x2A3808C23Eb2526E7f39C3AF8D917Eb5fE0Ef9Af,
            mintAmount: 44889288435523747478,
            depositAmount: 93025844243147440000
        });
        entries[145] = MintEntry({
            tokenId: 196,
            user: 0x2a5A2e72145118befd009EEb6a3BcABb120e321E,
            mintAmount: 299387390184388289349,
            depositAmount: 699232517750000000000
        });
        entries[146] = MintEntry({
            tokenId: 197,
            user: 0x2A70F4C0CF4c6ed5a2eA3E448d8a3aeDB1c494a7,
            mintAmount: 1731376230178223163,
            depositAmount: 40000000000000000000
        });
        entries[147] = MintEntry({
            tokenId: 199,
            user: 0x2Aca7B284CCB72127510D39B188b68823637D3c8,
            mintAmount: 1776691390626212818009,
            depositAmount: 3900000000000000000000
        });
        entries[148] = MintEntry({
            tokenId: 200,
            user: 0x2b2411BD9Dcfb0d3F375521917e623676987dFb1,
            mintAmount: 6985137720088044793841,
            depositAmount: 15421811496285209000000
        });
        entries[149] = MintEntry({
            tokenId: 201,
            user: 0x2B30ba56632093c6937B9440531cCA558F35FC93,
            mintAmount: 64428532304410353116,
            depositAmount: 300000000000000000000
        });
        entries[150] = MintEntry({
            tokenId: 202,
            user: 0x2B59FD03d176aFC335Fa6D4FBCDf5cF48a6844FB,
            mintAmount: 4563636568729047074,
            depositAmount: 10940269783365544000
        });
        entries[151] = MintEntry({
            tokenId: 203,
            user: 0x2B7340A45eB68592492295ED60983D0939D02B91,
            mintAmount: 68091606149935850587,
            depositAmount: 159799342655818830000
        });
        entries[152] = MintEntry({
            tokenId: 204,
            user: 0x2bd7aB7bDBC4eB1C88ACb8CeB80D805Fc0243EB5,
            mintAmount: 864444548896908688858,
            depositAmount: 2015853716481627000000
        });
        entries[153] = MintEntry({
            tokenId: 205,
            user: 0x2BEf163e00d5411C9BB67b08643E322f70B863C7,
            mintAmount: 150527127374122565878,
            depositAmount: 335580000000000000000
        });
        entries[154] = MintEntry({
            tokenId: 206,
            user: 0x2c066385B594a8871870F51CFc5845A2C2C4a0c6,
            mintAmount: 49581937575563456115,
            depositAmount: 124283040000000000000
        });
        entries[155] = MintEntry({
            tokenId: 207,
            user: 0x2C09D55D59956F6db6Ddfaa68962E87d1d92CE2E,
            mintAmount: 94669521912900831069,
            depositAmount: 624945724316840400000
        });
        entries[156] = MintEntry({
            tokenId: 208,
            user: 0x2Cddc815f81199dD128581e61f93688796c560d7,
            mintAmount: 326196527293502226531,
            depositAmount: 726945603516176300000
        });
        entries[157] = MintEntry({
            tokenId: 209,
            user: 0x2cdF675e966Ca6C95cEde42144F774031991a60A,
            mintAmount: 13611286302804760238405,
            depositAmount: 38590805380066580000000
        });
        entries[158] = MintEntry({
            tokenId: 210,
            user: 0x2d42AF353533fE0911E6d2046CE773BE2D758ce0,
            mintAmount: 21257534688475235359068,
            depositAmount: 43053958669255930000000
        });
        entries[159] = MintEntry({
            tokenId: 211,
            user: 0x2d7B10F39653321b77F6a53FF13BCdFd836DDa05,
            mintAmount: 771403612153051671373,
            depositAmount: 2094558561579879000000
        });
        entries[160] = MintEntry({
            tokenId: 212,
            user: 0x2DE55CCFBf37e76E536934e1C5B7164b12792C4D,
            mintAmount: 2110156915663218886585,
            depositAmount: 4576493118792770000000
        });
        entries[161] = MintEntry({
            tokenId: 213,
            user: 0x2E14450770d9B5DF25c4d816605a953Ec2Dd3e2B,
            mintAmount: 888741234580095513586,
            depositAmount: 1979800000000000000000
        });
        entries[162] = MintEntry({
            tokenId: 214,
            user: 0x2E2fb1C83812821805D2d69e1D8DA146B35E77a6,
            mintAmount: 398314399187710443354,
            depositAmount: 998942823606960000000
        });
        entries[163] = MintEntry({
            tokenId: 215,
            user: 0x2E31C90426eAFD0171561D130dbdF9f921273202,
            mintAmount: 2390164891723592714,
            depositAmount: 4999872272844234000
        });
        entries[164] = MintEntry({
            tokenId: 216,
            user: 0x2E765f16c376AC1C06d676cdA48392dfDB0Ee600,
            mintAmount: 20956841157671975677,
            depositAmount: 49990401840000000000
        });
        entries[165] = MintEntry({
            tokenId: 218,
            user: 0x2e96Bc789dbd3d1613Bf0D9462fc50fdE8b4dA0A,
            mintAmount: 1241893706288760848128,
            depositAmount: 3504466927342264000000
        });
        entries[166] = MintEntry({
            tokenId: 219,
            user: 0x2F386Be061537Dd52c25b14b1a6b33bd4e54b1F4,
            mintAmount: 39988407946226111306,
            depositAmount: 100000000000000000000
        });
        entries[167] = MintEntry({
            tokenId: 221,
            user: 0x2f9c8F825173daF5A68E6035440e1de57d69cB39,
            mintAmount: 507226274378090153662,
            depositAmount: 1142620027446645600000
        });
        entries[168] = MintEntry({
            tokenId: 223,
            user: 0x3009b326dCE73371eD4577567a7F34F5f1aD5c85,
            mintAmount: 114904063545444064232,
            depositAmount: 276633404063448400000
        });
        entries[169] = MintEntry({
            tokenId: 224,
            user: 0x302215755b3F07706489Edd77754d4AB53639228,
            mintAmount: 2409777545909405628653,
            depositAmount: 5399597150000000000000
        });
        entries[170] = MintEntry({
            tokenId: 225,
            user: 0x305a41F9582B704224240908D5880393C7C1CFc7,
            mintAmount: 63952253475988062152,
            depositAmount: 160000000000000000000
        });
        entries[171] = MintEntry({
            tokenId: 226,
            user: 0x30ad59Ef57A14aef057972DB43Fea3Cb1e2563ec,
            mintAmount: 48706033585234812706,
            depositAmount: 252929586295463200000
        });
        entries[172] = MintEntry({
            tokenId: 227,
            user: 0x30b14392B5c8DBe992E6D1D28dea0a612D152f33,
            mintAmount: 17621340643730934738,
            depositAmount: 47822760000000000000
        });
        entries[173] = MintEntry({
            tokenId: 228,
            user: 0x30c3545c8DF984704c85a06312aEfA4d415A2468,
            mintAmount: 131486548134311005596,
            depositAmount: 422970114835462800000
        });
        entries[174] = MintEntry({
            tokenId: 229,
            user: 0x30c79E90D8a4747d347488C81E8Fa0e629cf6153,
            mintAmount: 51365008228673191969,
            depositAmount: 147137723575860260000
        });
        entries[175] = MintEntry({
            tokenId: 230,
            user: 0x313bCC02f4BCAb75426706a148B457f160D1cE11,
            mintAmount: 36264022006855691824,
            depositAmount: 87196426974850370000
        });
        entries[176] = MintEntry({
            tokenId: 231,
            user: 0x319DE5a8824145B5f4953F21ADbF384cC75b77fE,
            mintAmount: 204866871826709030329,
            depositAmount: 495000000000000000000
        });
        entries[177] = MintEntry({
            tokenId: 233,
            user: 0x31f17C7f7B1De79b96A25c64CfB6450a5807574a,
            mintAmount: 150393573111830898853,
            depositAmount: 666000000000000000000
        });
        entries[178] = MintEntry({
            tokenId: 234,
            user: 0x324c88b7c20670cE4f53338fb08A1f97254eaE0c,
            mintAmount: 420016769148432290774,
            depositAmount: 1006572108151919200000
        });
        entries[179] = MintEntry({
            tokenId: 236,
            user: 0x327D5C63F2b885D1eD7804Eb3F00dc26276C0Fc5,
            mintAmount: 151238412739523291266,
            depositAmount: 362280000000000000000
        });
        entries[180] = MintEntry({
            tokenId: 237,
            user: 0x330C74Db36F36Ee03Acf90215050f06F397CB28f,
            mintAmount: 425131255731045238513,
            depositAmount: 1025532890535981600000
        });
        entries[181] = MintEntry({
            tokenId: 238,
            user: 0x3382A350C1e1Db5c306E10B4D750BF4668c12c65,
            mintAmount: 218424557894899770795,
            depositAmount: 479462479736203000000
        });
        entries[182] = MintEntry({
            tokenId: 242,
            user: 0x34993e20033cfE4280d8fAE0557cdd09042De668,
            mintAmount: 366870755491093461873,
            depositAmount: 1358651344422283000000
        });
        entries[183] = MintEntry({
            tokenId: 243,
            user: 0x3519585b5AFc6957e87B3F1968CAeC0A738ab785,
            mintAmount: 1639096646418695253171,
            depositAmount: 3554861000000000000000
        });
        entries[184] = MintEntry({
            tokenId: 244,
            user: 0x35340a9289E212C4FAaEd35A0De0e0Bc3D4028dD,
            mintAmount: 1613746712881913327616,
            depositAmount: 4978737090047363000000
        });
        entries[185] = MintEntry({
            tokenId: 245,
            user: 0x35359023AF331621460A038d0c0f300576093086,
            mintAmount: 68437176258254849029,
            depositAmount: 163949529506616380000
        });
        entries[186] = MintEntry({
            tokenId: 247,
            user: 0x358c84fAA7f860ab41b93edCcB7e64f7Eb330Bb1,
            mintAmount: 5056257062327413102396,
            depositAmount: 12500000000000000000000
        });
        entries[187] = MintEntry({
            tokenId: 248,
            user: 0x35dDE84C5eE1a2E08F8DE9890ea9f4a24cfCC32e,
            mintAmount: 292501605269348719253,
            depositAmount: 971400000000000000000
        });
        entries[188] = MintEntry({
            tokenId: 249,
            user: 0x35f44D96853145e8B86D939f914ab2eF5f11DA16,
            mintAmount: 62495402785441856364,
            depositAmount: 262611923471768000000
        });
        entries[189] = MintEntry({
            tokenId: 251,
            user: 0x361221F7F9C886Aff787CD4d4fAa3959dB9b0E9c,
            mintAmount: 97529747173545912850,
            depositAmount: 247000000000000000000
        });
        entries[190] = MintEntry({
            tokenId: 252,
            user: 0x372812E9891b2A8F2c8D7788ad3d90A0826d73c6,
            mintAmount: 8375196359749239726,
            depositAmount: 23221842897945800000
        });
        entries[191] = MintEntry({
            tokenId: 253,
            user: 0x37672b189Cc69fC47AdE93AAf4bdD75394CA69d5,
            mintAmount: 20229358982112704995,
            depositAmount: 48320161032982890000
        });
        entries[192] = MintEntry({
            tokenId: 254,
            user: 0x3771cE1CF0a910305af51606c88B95b06748762E,
            mintAmount: 7431914190562828310905,
            depositAmount: 14999985092217200000000
        });
        entries[193] = MintEntry({
            tokenId: 255,
            user: 0x37cACE97BBf0d68b391c0dA54B6fDFb137Bf07a3,
            mintAmount: 139160411516227871210,
            depositAmount: 310000000000000000000
        });
        entries[194] = MintEntry({
            tokenId: 256,
            user: 0x3813d76B2e9b3748afA4b7FC3A19f7b0318bA47B,
            mintAmount: 15626779932791829616292,
            depositAmount: 49950000000000000000000
        });
        entries[195] = MintEntry({
            tokenId: 257,
            user: 0x3815c846be224426eC3b704099fd2Ed9301d351a,
            mintAmount: 566672481348642297693,
            depositAmount: 1336713473677711000000
        });
        entries[196] = MintEntry({
            tokenId: 258,
            user: 0x38476bc1deb12F317cabC3F49fBBb80FbaB6f3ec,
            mintAmount: 67268479552875513432,
            depositAmount: 161209218891411360000
        });
        entries[197] = MintEntry({
            tokenId: 259,
            user: 0x38542c48F6eEbf09dD07902586D55ae4688A406e,
            mintAmount: 421585404928402458035,
            depositAmount: 973588271680000000000
        });
        entries[198] = MintEntry({
            tokenId: 260,
            user: 0x386fa844087aB11093a38C23A414e7d932699d9E,
            mintAmount: 23754561784167674250,
            depositAmount: 50000000000000000000
        });
        entries[199] = MintEntry({
            tokenId: 261,
            user: 0x38c2ecAb11d12A523E9be30C671F8C1f68947869,
            mintAmount: 223678124409607359912,
            depositAmount: 564261536000000000000
        });
        entries[200] = MintEntry({
            tokenId: 265,
            user: 0x3A271B7d12dfb1b36910b1f1Bdd352C281139DA1,
            mintAmount: 189577958932136090684,
            depositAmount: 747018892089404200000
        });
        entries[201] = MintEntry({
            tokenId: 266,
            user: 0x3a5dCe085D252C1eB7a1EF2C65636Ab5BE66AEa8,
            mintAmount: 190278011977297576265,
            depositAmount: 455529520390000000000
        });
        entries[202] = MintEntry({
            tokenId: 267,
            user: 0x3A6C0d15BE9E590e4e09311bA87aB96e23c44b8B,
            mintAmount: 2258115491187990184195,
            depositAmount: 7541803321643488000000
        });
        entries[203] = MintEntry({
            tokenId: 268,
            user: 0x3a92A585F903Ac79F6D41D971e3d76C207567aC4,
            mintAmount: 213293734488817790688,
            depositAmount: 510935951990000000000
        });
        entries[204] = MintEntry({
            tokenId: 269,
            user: 0x3b320Fc9e5B36FFa940c2Bb26cd632D8b511193A,
            mintAmount: 41037308657316086376,
            depositAmount: 117536253961628400000
        });
        entries[205] = MintEntry({
            tokenId: 271,
            user: 0x3B63BD52c7D2d56954428b2Cb75C573AE6010714,
            mintAmount: 733111987498115371309,
            depositAmount: 1999999396257925000000
        });
        entries[206] = MintEntry({
            tokenId: 272,
            user: 0x3B88C55F68AC330f6D5Fb229DC3A7EF5448b5e57,
            mintAmount: 78970894996610635862,
            depositAmount: 191000000000000000000
        });
        entries[207] = MintEntry({
            tokenId: 273,
            user: 0x3C6D5ac1CF91a7E7f99E9357E172b08583ACc446,
            mintAmount: 830668284466571060827,
            depositAmount: 2025853200000000000000
        });
        entries[208] = MintEntry({
            tokenId: 275,
            user: 0x3D3dC4B0445f1063644E9D0B2Ba1c66F7958f248,
            mintAmount: 3005303960725654763933,
            depositAmount: 6749482097417236000000
        });
        entries[209] = MintEntry({
            tokenId: 276,
            user: 0x3D496dbFe711A3fe668Cf08b5f4a3FEF1b696A39,
            mintAmount: 88981609409733236053,
            depositAmount: 199299912600000000000
        });
        entries[210] = MintEntry({
            tokenId: 278,
            user: 0x3d78B9f4e7D591238434a0c263a68b8EE00FD295,
            mintAmount: 13784341330666131952,
            depositAmount: 33000000000000000000
        });
        entries[211] = MintEntry({
            tokenId: 280,
            user: 0x3EbB29c47D64B70599BC37E2ea15d9E1eC1A07fC,
            mintAmount: 912351522205181713747,
            depositAmount: 1941000345110608000000
        });
        entries[212] = MintEntry({
            tokenId: 281,
            user: 0x3ebf6C0EfF9d69fCB7F129f090c223639a5de234,
            mintAmount: 853550516195215095425,
            depositAmount: 1850000000000000000000
        });
        entries[213] = MintEntry({
            tokenId: 283,
            user: 0x3f5351436afCF23D25d28F945CaC4A35bD223fFe,
            mintAmount: 254446527088789679246,
            depositAmount: 980208758000000000000
        });
        entries[214] = MintEntry({
            tokenId: 284,
            user: 0x402904E954aebEE2E78b7B09595393cf05571333,
            mintAmount: 5308551809156207844014,
            depositAmount: 10663357805874860000000
        });
        entries[215] = MintEntry({
            tokenId: 285,
            user: 0x40507E76E535413A2aB804e2e16462a99D2b6Ffc,
            mintAmount: 41718049239334186807,
            depositAmount: 100000000000000000000
        });
        entries[216] = MintEntry({
            tokenId: 286,
            user: 0x4050Fb99522a60E9AB875935Fcf6D211c17d98c3,
            mintAmount: 959169349678563836,
            depositAmount: 1995948073975080700
        });
        entries[217] = MintEntry({
            tokenId: 288,
            user: 0x40ABa0420d6B49AD8449c83a65Ef1025cd845C79,
            mintAmount: 429412498652044776610,
            depositAmount: 1085000000000000000000
        });
        entries[218] = MintEntry({
            tokenId: 289,
            user: 0x40Be96BD01023cFED176a12112d60Fd3daCDa425,
            mintAmount: 229094464254084949349,
            depositAmount: 543811321226083400000
        });
        entries[219] = MintEntry({
            tokenId: 290,
            user: 0x40C3fee191c0eb74525d94e8693146b9714e2Ad8,
            mintAmount: 398884369263614435279,
            depositAmount: 997500000000000000000
        });
        entries[220] = MintEntry({
            tokenId: 292,
            user: 0x4141EC9F8Acfd636E7b037EB3171f4452656dA35,
            mintAmount: 417115118938594524484,
            depositAmount: 998631874330000000000
        });
        entries[221] = MintEntry({
            tokenId: 293,
            user: 0x41BEadcd262722361E9054D2Ad8BdA41A913816a,
            mintAmount: 139782204662083904231,
            depositAmount: 397841216706444800000
        });
        entries[222] = MintEntry({
            tokenId: 294,
            user: 0x420820080Eb561da3962407AF781cb05dd727f4B,
            mintAmount: 121942449607719048676,
            depositAmount: 282494045470000000000
        });
        entries[223] = MintEntry({
            tokenId: 295,
            user: 0x42a8Db3E02e5d47cd8f56646b8ccA18948488FE7,
            mintAmount: 31922764224123494972,
            depositAmount: 84746018122951160000
        });
        entries[224] = MintEntry({
            tokenId: 296,
            user: 0x42B5274Cc92E479f1F36001939D18f74B61836aA,
            mintAmount: 48777318445438308748,
            depositAmount: 100000000000000000000
        });
        entries[225] = MintEntry({
            tokenId: 298,
            user: 0x43093861E897D139342CE149935a5f721532a660,
            mintAmount: 91014958464774368913,
            depositAmount: 283359331926622100000
        });
        entries[226] = MintEntry({
            tokenId: 299,
            user: 0x432D28A6857cf484EbF0ddC1dA698f20D48CDe13,
            mintAmount: 116925088806495653270,
            depositAmount: 375077975981561800000
        });
        entries[227] = MintEntry({
            tokenId: 300,
            user: 0x435C47de292a9aCE3BF8D0F4A333a4865988ec3D,
            mintAmount: 52959586341984934505,
            depositAmount: 127319141218550090000
        });
        entries[228] = MintEntry({
            tokenId: 301,
            user: 0x43b69B1f81e4DB49469B73304B9De01b035679F6,
            mintAmount: 190354444764462726243,
            depositAmount: 499531521310575030000
        });
        entries[229] = MintEntry({
            tokenId: 302,
            user: 0x43dEcad5db1faa9DF795fF24DD4fD548749a1aC2,
            mintAmount: 75716360410380086226,
            depositAmount: 189804117770000000000
        });
        entries[230] = MintEntry({
            tokenId: 303,
            user: 0x44031A2Aa10C80f1246d32a67304D233651148AB,
            mintAmount: 275628163646026661739,
            depositAmount: 666932117690404400000
        });
        entries[231] = MintEntry({
            tokenId: 304,
            user: 0x44299097358A1aBD676f06015c6243f6D73fafC5,
            mintAmount: 4117806830216186074,
            depositAmount: 8442052497868067000
        });
        entries[232] = MintEntry({
            tokenId: 306,
            user: 0x4463A42FF655B6B92BCB82cD230A55EBaA3E3D46,
            mintAmount: 426816276538312052288,
            depositAmount: 984099900000000000000
        });
        entries[233] = MintEntry({
            tokenId: 307,
            user: 0x446Dfb13B284ec15BF1F88b7edbbeBa8c3B82122,
            mintAmount: 47999508722515758354,
            depositAmount: 114280530000000000000
        });
        entries[234] = MintEntry({
            tokenId: 309,
            user: 0x44B90068f77f16E321B22A8cd68243106E6c2cE0,
            mintAmount: 132315899662739748654,
            depositAmount: 358999784194471360000
        });
        entries[235] = MintEntry({
            tokenId: 310,
            user: 0x44c88c923165D03d8d8583F64667570C74229Dd2,
            mintAmount: 650336239459757610543,
            depositAmount: 1683125683716849400000
        });
        entries[236] = MintEntry({
            tokenId: 311,
            user: 0x44CfAD901D9E302138C49bC27f53b9EB2d9d8BB6,
            mintAmount: 777614932401886385288,
            depositAmount: 2059377122010000000000
        });
        entries[237] = MintEntry({
            tokenId: 312,
            user: 0x45037a8feBd841FeFaf6D451bc743a99c9749A93,
            mintAmount: 447744876004571997792,
            depositAmount: 1076414999350441100000
        });
        entries[238] = MintEntry({
            tokenId: 313,
            user: 0x456Eb5DaAC06b24A361717ED6Dc759438464c18A,
            mintAmount: 6282525786974950971,
            depositAmount: 15000000000000000000
        });
        entries[239] = MintEntry({
            tokenId: 314,
            user: 0x45752b31849304a6170add14DB59F0d4B85EcAd0,
            mintAmount: 916769376912316700195,
            depositAmount: 1854419765715119600000
        });
        entries[240] = MintEntry({
            tokenId: 315,
            user: 0x45C7811C459a43d0C17EF18F33A2C8921aC4ECf8,
            mintAmount: 32813565434821537154,
            depositAmount: 78256581159663800000
        });
        entries[241] = MintEntry({
            tokenId: 316,
            user: 0x46026Bb1F8a9c5cf418DB02226696784D8DF6aeD,
            mintAmount: 417830095624232288071,
            depositAmount: 996476742343520000000
        });
        entries[242] = MintEntry({
            tokenId: 317,
            user: 0x461516b09A2DF2D3bf8e1945d448A105E635A3c7,
            mintAmount: 36975608630540687406,
            depositAmount: 100000000000000000000
        });
        entries[243] = MintEntry({
            tokenId: 320,
            user: 0x46BBB9F5de1E854a80bDA9E2596C4d2530418b99,
            mintAmount: 368471845701333150059,
            depositAmount: 1000000000000000000000
        });
        entries[244] = MintEntry({
            tokenId: 321,
            user: 0x46f76fcD02Ac4AA4Fb864F5a08D95A52A9e74A45,
            mintAmount: 514170345520399498066,
            depositAmount: 1234275261995247700000
        });
        entries[245] = MintEntry({
            tokenId: 322,
            user: 0x4710E5487f22b7687983E7e38085aa9d78617BB8,
            mintAmount: 383862980640572124245,
            depositAmount: 984993272980000000000
        });
        entries[246] = MintEntry({
            tokenId: 323,
            user: 0x4728aA2DaEa1F4ED0A72c2c2Ef586915C54a887d,
            mintAmount: 81507239088018880936,
            depositAmount: 190679588930201650000
        });
        entries[247] = MintEntry({
            tokenId: 324,
            user: 0x474AF76116B5F1DAb3b3B4c670f32b87B649C5B7,
            mintAmount: 2523297973653448779,
            depositAmount: 6000000000000000000
        });
        entries[248] = MintEntry({
            tokenId: 325,
            user: 0x476ee7190CbE2307Df10E3b3d10f37b5212357c1,
            mintAmount: 704348598603579004871,
            depositAmount: 2150000000000000000000
        });
        entries[249] = MintEntry({
            tokenId: 326,
            user: 0x477c2087F3D6e49b1BE5C790A33b3a025A4Fa569,
            mintAmount: 15837541443282518294,
            depositAmount: 37957482868903050000
        });
        entries[250] = MintEntry({
            tokenId: 327,
            user: 0x47972b9C9445EF20E8A3bd86AFb0476993488a56,
            mintAmount: 39920874319488067308,
            depositAmount: 95439547280000000000
        });
        entries[251] = MintEntry({
            tokenId: 328,
            user: 0x481b63197922715893Ec4ed82ccdA4FaA4af570C,
            mintAmount: 26693616608218508935,
            depositAmount: 99999887450180000000
        });
        entries[252] = MintEntry({
            tokenId: 329,
            user: 0x482d3329eb3Ab650c151e41B9ECB1D9F222909Ea,
            mintAmount: 44849568836970999309,
            depositAmount: 102533129024312280000
        });
        entries[253] = MintEntry({
            tokenId: 330,
            user: 0x483B0FB09862d45b0C97D94AEB3684A95B4DfE85,
            mintAmount: 27925318683795941413610,
            depositAmount: 72535110414238200000000
        });
        entries[254] = MintEntry({
            tokenId: 331,
            user: 0x486843aD8adb101584FCcE56E88a09e6f25D16d1,
            mintAmount: 197094179170771917239,
            depositAmount: 476460279000000000000
        });
        entries[255] = MintEntry({
            tokenId: 332,
            user: 0x491180FaC09C5A3f76e2Abc2dffaae4500b73Aa5,
            mintAmount: 38690568929367214601,
            depositAmount: 92000000000000000000
        });
        entries[256] = MintEntry({
            tokenId: 333,
            user: 0x4920BF9F132eB5B7ae6339bBB50A3c6E00C94D0f,
            mintAmount: 302466162266876248986,
            depositAmount: 723521812547905700000
        });
        entries[257] = MintEntry({
            tokenId: 336,
            user: 0x4a7fA3c40d2CeBA1dcB9463feF1552dB0365a864,
            mintAmount: 190859962171455794857,
            depositAmount: 391288345186399200000
        });
        entries[258] = MintEntry({
            tokenId: 337,
            user: 0x4A8ADfC511F800df904B0536354c4038DD3BB74A,
            mintAmount: 310183715524087350918,
            depositAmount: 691260235519494700000
        });
        entries[259] = MintEntry({
            tokenId: 338,
            user: 0x4ABc33CF81e0d21f42168d044f7002eDd6b80B09,
            mintAmount: 14901717113315913563797,
            depositAmount: 42030390096223500000000
        });
        entries[260] = MintEntry({
            tokenId: 339,
            user: 0x4ABdF936E1dD632dBdF44079c8E850cdF848B802,
            mintAmount: 18398991125814849835,
            depositAmount: 46143298319678020000
        });
        entries[261] = MintEntry({
            tokenId: 340,
            user: 0x4AF889460AdCaFe14fE17CC51Af60D2E173BD0C5,
            mintAmount: 49499605465933592489,
            depositAmount: 118554881899458840000
        });
        entries[262] = MintEntry({
            tokenId: 341,
            user: 0x4B03aF034512f9535084e44F3cbA700E8efe12A2,
            mintAmount: 4105674477178530854,
            depositAmount: 8899459565921322000
        });
        entries[263] = MintEntry({
            tokenId: 342,
            user: 0x4b66277b7Be642D9b7D5cB8eECBBD6F001e5a961,
            mintAmount: 88213554073975961128,
            depositAmount: 209901738431026000000
        });
        entries[264] = MintEntry({
            tokenId: 344,
            user: 0x4BdE1498d267a7763635A7f2DCECD67f5bB69d49,
            mintAmount: 7695173739474742618,
            depositAmount: 18286690000000000000
        });
        entries[265] = MintEntry({
            tokenId: 345,
            user: 0x4c3C99B358b338F1e3A281d1aecAfaA8305E4759,
            mintAmount: 410164126529542153640,
            depositAmount: 982049590000000000000
        });
        entries[266] = MintEntry({
            tokenId: 346,
            user: 0x4C3CF435f258d73473c53B3feC02fA7DFa0B453f,
            mintAmount: 223194726743985621023,
            depositAmount: 500000000000000000000
        });
        entries[267] = MintEntry({
            tokenId: 347,
            user: 0x4C528ACa678664d62E5b92b0B5973e5aF00fDc75,
            mintAmount: 10970552441762562080,
            depositAmount: 26388965996131880000
        });
        entries[268] = MintEntry({
            tokenId: 348,
            user: 0x4c6996F712f5Ba388C0F2930d05fc8746a2CDB0D,
            mintAmount: 2976025940190412621994,
            depositAmount: 6070154318355478000000
        });
        entries[269] = MintEntry({
            tokenId: 350,
            user: 0x4C735d3Acba20B72d3D1b11C3Cc3ce00377906aE,
            mintAmount: 495225817930433688434,
            depositAmount: 1389791706211613000000
        });
        entries[270] = MintEntry({
            tokenId: 351,
            user: 0x4cd02F464Ddea99fA5f71FBA239E681c278Cf1cF,
            mintAmount: 4947154349996443585,
            depositAmount: 10983665152725000000
        });
        entries[271] = MintEntry({
            tokenId: 352,
            user: 0x4CD6bdCC4aBd55a546c8f416234e1ec6495a6478,
            mintAmount: 1238607790689159832174,
            depositAmount: 2508811861799376000000
        });
        entries[272] = MintEntry({
            tokenId: 354,
            user: 0x4CdF040935a1f3c6424F96cda3A3b748DD9213A1,
            mintAmount: 2196856433319172191,
            depositAmount: 6000000000000000000
        });
        entries[273] = MintEntry({
            tokenId: 355,
            user: 0x4d302879bD999E42c65D75dDD13031AeF9C895E1,
            mintAmount: 1277824804875859073035,
            depositAmount: 2659042388108280000000
        });
        entries[274] = MintEntry({
            tokenId: 356,
            user: 0x4D5fA23842091BED38aC4C0acb2BA28ac55E48E4,
            mintAmount: 116973708503517063586,
            depositAmount: 282632253780000000000
        });
        entries[275] = MintEntry({
            tokenId: 357,
            user: 0x4D6cACa69591614B58f6AbB343774F913F4FcCC7,
            mintAmount: 18305130004584815901413,
            depositAmount: 40033402915765890000000
        });
        entries[276] = MintEntry({
            tokenId: 358,
            user: 0x4D9edF8E965612662C6f25D0CdeA199b42cB278d,
            mintAmount: 409186417435548053942,
            depositAmount: 987369774431343000000
        });
        entries[277] = MintEntry({
            tokenId: 359,
            user: 0x4E09eC5a56eB368111d48Ea699AAc23FEAd87961,
            mintAmount: 9020197852400798573958,
            depositAmount: 32104297433848942000000
        });
        entries[278] = MintEntry({
            tokenId: 361,
            user: 0x4Ebb80FD8c0ad32600985B8FdF6A0DFE083e9e13,
            mintAmount: 3327284727012519030822,
            depositAmount: 7500000000000000000000
        });
        entries[279] = MintEntry({
            tokenId: 362,
            user: 0x4f0c471B37069C55783707a8DE571711A9C6405e,
            mintAmount: 83767010493011679613,
            depositAmount: 200000000000000000000
        });
        entries[280] = MintEntry({
            tokenId: 363,
            user: 0x4F8E725B6EbA799e2445760c6C21bFdE945A141a,
            mintAmount: 1017935430718646607325,
            depositAmount: 2584295623711414300000
        });
        entries[281] = MintEntry({
            tokenId: 364,
            user: 0x4fC4D16b8dD58AE3fa7aAc8fF29336D17F199f97,
            mintAmount: 2753527949249493581255,
            depositAmount: 6571119951677284000000
        });
        entries[282] = MintEntry({
            tokenId: 365,
            user: 0x50bBBd037d41cABe7228f58bB29dC9c7bC33664F,
            mintAmount: 317839287421379182294,
            depositAmount: 760747699058380200000
        });
        entries[283] = MintEntry({
            tokenId: 370,
            user: 0x51f8d3875C0fdb3a36dE5CF24DD359F4700FFF16,
            mintAmount: 16622484820448787413,
            depositAmount: 39072063010281500000
        });
        entries[284] = MintEntry({
            tokenId: 371,
            user: 0x5224DF5A8cC89F3DC728e54Dc239dC828D474f0C,
            mintAmount: 16768691897893914523,
            depositAmount: 40000000000000000000
        });
        entries[285] = MintEntry({
            tokenId: 372,
            user: 0x5269F2cA1A4e77c6C30EA5e732f55937B841ea60,
            mintAmount: 39799527854716058692,
            depositAmount: 90950000000000000000
        });
        entries[286] = MintEntry({
            tokenId: 374,
            user: 0x528018c88448f67D2B618a43546CF7e0B026857E,
            mintAmount: 15543582024467577467,
            depositAmount: 42000000000000000000
        });
        entries[287] = MintEntry({
            tokenId: 375,
            user: 0x52a0FA7Fb3E85F273A7D16Ba5285192fCDEe60Db,
            mintAmount: 38684197646736093371,
            depositAmount: 84200000000000000000
        });
        entries[288] = MintEntry({
            tokenId: 378,
            user: 0x53090863f818A63178fa9806AF701c81A3691701,
            mintAmount: 7495038141359620985709,
            depositAmount: 24191830614632496000000
        });
        entries[289] = MintEntry({
            tokenId: 379,
            user: 0x533d01A9c2Bc36034623407be7d28AC0c705899b,
            mintAmount: 1751178300278994360343,
            depositAmount: 5214911909989536000000
        });
        entries[290] = MintEntry({
            tokenId: 381,
            user: 0x548828926A44a457815F806e05788C2E11e1b9D6,
            mintAmount: 5770172146972025645876,
            depositAmount: 12500022503243434000000
        });
        entries[291] = MintEntry({
            tokenId: 382,
            user: 0x5494E6e91bBEd551199A1726d61d930C46b12EfA,
            mintAmount: 13193244716790603287231,
            depositAmount: 38233631259356260000000
        });
        entries[292] = MintEntry({
            tokenId: 383,
            user: 0x54BeCc7560a7Be76d72ED76a1f5fee6C5a2A7Ab6,
            mintAmount: 1594653106773750340840,
            depositAmount: 3477835565244176400000
        });
        entries[293] = MintEntry({
            tokenId: 384,
            user: 0x55126aB05C76fF8dEC5FA6d857AC25d366F0CA12,
            mintAmount: 28469252703778158709751,
            depositAmount: 81790532352269500000000
        });
        entries[294] = MintEntry({
            tokenId: 386,
            user: 0x551E06aF1c492655Bb9F15C9B12459386B5cE015,
            mintAmount: 45916394570845089983,
            depositAmount: 99559359633983680000
        });
        entries[295] = MintEntry({
            tokenId: 387,
            user: 0x554DDFABaB2524A229070E01e9FaaD627e4Ac513,
            mintAmount: 80284868335928907678,
            depositAmount: 193072160000000000000
        });
        entries[296] = MintEntry({
            tokenId: 388,
            user: 0x554EF8185467480Dc23b8c6DfD90794d1b340fBA,
            mintAmount: 11168940750494982345,
            depositAmount: 25185378825480280000
        });
        entries[297] = MintEntry({
            tokenId: 390,
            user: 0x55B473AC430bccd24e4c547d30dae582Db4dE434,
            mintAmount: 20012244364069531282,
            depositAmount: 47681948000000000000
        });
        entries[298] = MintEntry({
            tokenId: 392,
            user: 0x56640BA14fB770f1ED151886AC7BB6aDAa96955C,
            mintAmount: 236384044732439064519,
            depositAmount: 639999452365795000000
        });
        entries[299] = MintEntry({
            tokenId: 393,
            user: 0x56a5AB463B0856b520f750b657A71Dd13B000312,
            mintAmount: 17134103470517544151443,
            depositAmount: 49810929500184110000000
        });
        entries[300] = MintEntry({
            tokenId: 394,
            user: 0x57733c1C021589C664C3F54961f81eC103d6538E,
            mintAmount: 692153667005633177844,
            depositAmount: 1770000000000000000000
        });
        entries[301] = MintEntry({
            tokenId: 395,
            user: 0x5773A379F9f9870E1498d3e84fD4797d6b038C63,
            mintAmount: 491076317715322641719,
            depositAmount: 1043363384729884400000
        });
        entries[302] = MintEntry({
            tokenId: 398,
            user: 0x58e4e9D30Da309624c785069A99709b16276B196,
            mintAmount: 48718835894144083997,
            depositAmount: 99999904577595000000
        });
        entries[303] = MintEntry({
            tokenId: 399,
            user: 0x5989F02eC7b79D69BE8a3f6680486fC5708940Ca,
            mintAmount: 84766625678411956811,
            depositAmount: 200000000000000000000
        });
        entries[304] = MintEntry({
            tokenId: 400,
            user: 0x59E29369C791A696d1479198B772F95E96b7aDcC,
            mintAmount: 72509194632469791558,
            depositAmount: 155893776120000000000
        });
        entries[305] = MintEntry({
            tokenId: 401,
            user: 0x5A50412aD703847130469C1C4309abD411Ee0aD7,
            mintAmount: 21040367992992107603,
            depositAmount: 50000000000000000000
        });
        entries[306] = MintEntry({
            tokenId: 402,
            user: 0x5A97f8Db19C10BFf32A550cca2FE30c499293800,
            mintAmount: 65709113772937062408,
            depositAmount: 160000000000000000000
        });
        entries[307] = MintEntry({
            tokenId: 403,
            user: 0x5aB0e4E355b08e692933c1F6f85fd0bE56aD18A6,
            mintAmount: 557948960801040005692,
            depositAmount: 1575653715919081300000
        });
        entries[308] = MintEntry({
            tokenId: 404,
            user: 0x5ae344A53e47103c21127ae4386B94F5172B23Aa,
            mintAmount: 21691353917399041066,
            depositAmount: 47376766753676400000
        });
        entries[309] = MintEntry({
            tokenId: 405,
            user: 0x5aFd1bffd44eEb6A7853886bA3466c1df5a86F88,
            mintAmount: 19809605044106930421,
            depositAmount: 47095658650340300000
        });
        entries[310] = MintEntry({
            tokenId: 406,
            user: 0x5b1A102A8F82fd2C1231Fca763a7170920F7a7E3,
            mintAmount: 4865604050928102124,
            depositAmount: 11429135179264680000
        });
        entries[311] = MintEntry({
            tokenId: 407,
            user: 0x5B34b78F8dA6046EC9467e6DaC6E31C2d138690A,
            mintAmount: 6418201312700030202313,
            depositAmount: 20329193491000000000000
        });
        entries[312] = MintEntry({
            tokenId: 408,
            user: 0x5B66d58242476d7EB26bA35E5797F44D7D73e650,
            mintAmount: 359884691045660678936,
            depositAmount: 1000008460866890400000
        });
        entries[313] = MintEntry({
            tokenId: 410,
            user: 0x5c4C53a58790834Cc9D30807b8a7E1bF7Fa9F5C3,
            mintAmount: 84109932455147292612,
            depositAmount: 200000000000000000000
        });
        entries[314] = MintEntry({
            tokenId: 411,
            user: 0x5c530a5462abE16Fef4A3Ae7B0CdD1cab8DC1e67,
            mintAmount: 3604769267359031647181,
            depositAmount: 11064801447533292000000
        });
        entries[315] = MintEntry({
            tokenId: 413,
            user: 0x5cb559426C904e6b4d4ec4908C5c12217Fc6Fe8E,
            mintAmount: 3424058171235188038,
            depositAmount: 8925450594740000000
        });
        entries[316] = MintEntry({
            tokenId: 414,
            user: 0x5cC3cB20B2531C4A6d59Bf37aac8aCD0e8D099d3,
            mintAmount: 519445146266922452871,
            depositAmount: 1184314067820000000000
        });
        entries[317] = MintEntry({
            tokenId: 416,
            user: 0x5d4272799D45c325c115442e54688A416dE87094,
            mintAmount: 5428134533866595384356,
            depositAmount: 12013772062896226000000
        });
        entries[318] = MintEntry({
            tokenId: 417,
            user: 0x5D7166EE0C633021Cb502fa5302866316d86f701,
            mintAmount: 4500776966307730057,
            depositAmount: 12054022803250000000
        });
        entries[319] = MintEntry({
            tokenId: 418,
            user: 0x5d81AE293cBebdCD0fe57F62068bB763E56581AC,
            mintAmount: 23040542848627488316,
            depositAmount: 55234405922322250000
        });
        entries[320] = MintEntry({
            tokenId: 419,
            user: 0x5D9ed9cD7d7Bf4B6020811A0417392c26dD6FE01,
            mintAmount: 229291673894694593802,
            depositAmount: 586626600799068200000
        });
        entries[321] = MintEntry({
            tokenId: 420,
            user: 0x5dA8AD0AE65b7a7E1af12A32bBE46Da8B776f694,
            mintAmount: 1174828817064545091722,
            depositAmount: 2352048299945376000000
        });
        entries[322] = MintEntry({
            tokenId: 423,
            user: 0x5E5633046A35C8B2842DED8bb91c6a4bb1Cf4F08,
            mintAmount: 84398317840449491891,
            depositAmount: 199000000000000000000
        });
        entries[323] = MintEntry({
            tokenId: 424,
            user: 0x5e6E363eED7f6765A2165fAA46cd53b3ab3E000f,
            mintAmount: 8024349591186896544360,
            depositAmount: 20914911569212890000000
        });
        entries[324] = MintEntry({
            tokenId: 425,
            user: 0x5e765C6A318502FF2F6eF0D951e84F8dAE7FA3c9,
            mintAmount: 123192740530088321260,
            depositAmount: 292407728802449700000
        });
        entries[325] = MintEntry({
            tokenId: 426,
            user: 0x5E93781e8BAc02c42D1Efb9C80c7b9962ca66215,
            mintAmount: 11903657104755468724,
            depositAmount: 29013304303532843000
        });
        entries[326] = MintEntry({
            tokenId: 427,
            user: 0x5e945fE1851a2bFC86d618e200708D6209Bb9Bb6,
            mintAmount: 3818830708510436737003,
            depositAmount: 8576546611256839000000
        });
        entries[327] = MintEntry({
            tokenId: 428,
            user: 0x5ea61c2d641Faf0368dEB0c0790DD6A4eE8B23fF,
            mintAmount: 432158355062388766887,
            depositAmount: 1285766741728673400000
        });
        entries[328] = MintEntry({
            tokenId: 429,
            user: 0x5EA7D2F38BBDF1596Bad1DE3E10E79C1F0520129,
            mintAmount: 125765189234210858915,
            depositAmount: 300000000000000000000
        });
        entries[329] = MintEntry({
            tokenId: 430,
            user: 0x5ED15e97a35fFdB55903eE4Cd1B0D83E50dc46Fd,
            mintAmount: 181487567901812304181,
            depositAmount: 480638076370000000000
        });
        entries[330] = MintEntry({
            tokenId: 431,
            user: 0x5eDa263BffDcD20f26D2bF0f76b910d3FdCF5285,
            mintAmount: 41086040340875195771,
            depositAmount: 95883235829876420000
        });
        entries[331] = MintEntry({
            tokenId: 432,
            user: 0x5f69F630eefD1bD2f001f5C82EC643BF266E04C2,
            mintAmount: 441289110871350569670,
            depositAmount: 1200000000000000000000
        });
        entries[332] = MintEntry({
            tokenId: 434,
            user: 0x5fa8D894Acc5CfbE3933Fc0aE9052E786ce67b27,
            mintAmount: 214138822261695655430,
            depositAmount: 509836428600000000000
        });
        entries[333] = MintEntry({
            tokenId: 436,
            user: 0x5fCd5207FC508FD25dB690f3A349b1A8f4040870,
            mintAmount: 6202935225333269897962,
            depositAmount: 15372430873174565000000
        });
        entries[334] = MintEntry({
            tokenId: 437,
            user: 0x5fF2eBE49242A0d83dB1D50a6315C224a1a2e094,
            mintAmount: 11150089016324730448,
            depositAmount: 23087008751062100000
        });
        entries[335] = MintEntry({
            tokenId: 439,
            user: 0x605B5F6549538a94Bd2653d1EE67612a47039da0,
            mintAmount: 59754580585885377203542,
            depositAmount: 124204099121390140000000
        });
        entries[336] = MintEntry({
            tokenId: 441,
            user: 0x60C31519B80C75BdAE48E2512cB90B74F3c8F029,
            mintAmount: 37914128209907931685,
            depositAmount: 90000000000000000000
        });
        entries[337] = MintEntry({
            tokenId: 442,
            user: 0x61a50F6a1aD8AAb8efce0036470adfD8CEeF65F8,
            mintAmount: 371456563928405735491,
            depositAmount: 1000000000000000000000
        });
        entries[338] = MintEntry({
            tokenId: 443,
            user: 0x61C78Ec135598ac48754114f8A7B32A9E23816d1,
            mintAmount: 55337072109414283863,
            depositAmount: 134000000000000000000
        });
        entries[339] = MintEntry({
            tokenId: 444,
            user: 0x61cb6229936903b3c9281715aec32b5A54e3E648,
            mintAmount: 50846109132522869808,
            depositAmount: 118753341230000000000
        });
        entries[340] = MintEntry({
            tokenId: 445,
            user: 0x61FdECBFe6c572Ca3f631A8056d8322F9b12B7D9,
            mintAmount: 129113102886116289371,
            depositAmount: 347069478595000000000
        });
        entries[341] = MintEntry({
            tokenId: 446,
            user: 0x625fC4878A9086b017c6Bb5CB14310Ff78c62cdE,
            mintAmount: 187430642382265650158,
            depositAmount: 445873648274590900000
        });
        entries[342] = MintEntry({
            tokenId: 448,
            user: 0x62d51Fa08B15411D9429133aE5F224abf3867729,
            mintAmount: 44855810052482332105,
            depositAmount: 100000000000000000000
        });
        entries[343] = MintEntry({
            tokenId: 450,
            user: 0x637cc27ecd949b50625f0C0633b5d993C62758De,
            mintAmount: 69120623408028378877,
            depositAmount: 165379238429655200000
        });
        entries[344] = MintEntry({
            tokenId: 451,
            user: 0x63Adb116296dF047E3f4EfE913B04783e3d20F0A,
            mintAmount: 7591040495070901415,
            depositAmount: 20113263742690324000
        });
        entries[345] = MintEntry({
            tokenId: 452,
            user: 0x63b8065be25E50a53BBF88BdFa116ba206272a51,
            mintAmount: 58626141050499138978,
            depositAmount: 148716500164189980000
        });
        entries[346] = MintEntry({
            tokenId: 454,
            user: 0x63be84b1d75751E52716aE153Dbc5aBB5B2a98f5,
            mintAmount: 65407822314420880489,
            depositAmount: 165077014999646630000
        });
        entries[347] = MintEntry({
            tokenId: 455,
            user: 0x63FD238428938e4c085853c56C990A64aeA7F5d8,
            mintAmount: 11882948447722157451,
            depositAmount: 24999981545893850000
        });
        entries[348] = MintEntry({
            tokenId: 456,
            user: 0x6456B1425a918F5C7558F02546a9E6b247535f21,
            mintAmount: 202836032645114656523,
            depositAmount: 464000000000000000000
        });
        entries[349] = MintEntry({
            tokenId: 459,
            user: 0x64ba57bF7977DC2c60a5C9935E01E2bc6cf638cA,
            mintAmount: 13456490960039703552,
            depositAmount: 36226378889636760000
        });
        entries[350] = MintEntry({
            tokenId: 460,
            user: 0x64Cf6d15EA749ccB20032217D8a18B7a820956df,
            mintAmount: 34561041800325747220,
            depositAmount: 91749907814848400000
        });
        entries[351] = MintEntry({
            tokenId: 461,
            user: 0x6543B529094eE8aC9ed9AA81f455De34Cc3bE0A7,
            mintAmount: 4079284010323853781770,
            depositAmount: 10749907262742905000000
        });
        entries[352] = MintEntry({
            tokenId: 463,
            user: 0x65674eB175A6A101cbc45A934492B77a1E0d9b9C,
            mintAmount: 1736224768411042264460,
            depositAmount: 4004856331111301000000
        });
        entries[353] = MintEntry({
            tokenId: 464,
            user: 0x656b003aeDC30D2ef61D6D111e2F7956E0CA88f1,
            mintAmount: 68002345963112684015,
            depositAmount: 250000000000000000000
        });
        entries[354] = MintEntry({
            tokenId: 465,
            user: 0x65ef71Aa063cEcEB6569b9fdcd632952B2F141D9,
            mintAmount: 9085724698397837195,
            depositAmount: 19999889089661590000
        });
        entries[355] = MintEntry({
            tokenId: 466,
            user: 0x65F570384d6cC157A15eac9Bfd9DA88364D59b7F,
            mintAmount: 72519997358201601679964,
            depositAmount: 146889944465352890000000
        });
        entries[356] = MintEntry({
            tokenId: 467,
            user: 0x665d2D2444f2384fB3d96aaA0ea3536B92984dce,
            mintAmount: 16137590508820053161,
            depositAmount: 40374096940630690000
        });
        entries[357] = MintEntry({
            tokenId: 469,
            user: 0x66E678F79498d934F4d4BEDEE496adeb9B6b2C34,
            mintAmount: 560667961614806932,
            depositAmount: 1500000000000000000
        });
        entries[358] = MintEntry({
            tokenId: 470,
            user: 0x67136B2e605eda181fB035fE326e429479EfC484,
            mintAmount: 105062757683441362662,
            depositAmount: 252290642960654700000
        });
        entries[359] = MintEntry({
            tokenId: 471,
            user: 0x67576c519e804E02da310c2af7d93F3Adb0e441d,
            mintAmount: 102142137603809072150,
            depositAmount: 244637284410512080000
        });
        entries[360] = MintEntry({
            tokenId: 473,
            user: 0x67d019eBf6D76AFE2ee07781bD882989136b08c2,
            mintAmount: 2781637146910750445248,
            depositAmount: 8242300329940000000000
        });
        entries[361] = MintEntry({
            tokenId: 475,
            user: 0x6815084e9b2abb657b377f6DcA85ee7A1d2C1d89,
            mintAmount: 9225369946225308682,
            depositAmount: 20000000000000000000
        });
        entries[362] = MintEntry({
            tokenId: 476,
            user: 0x682d9234388E77c598d6ef5C477B90Dd766C1cC8,
            mintAmount: 209595291113018912885,
            depositAmount: 501148930000000000000
        });
        entries[363] = MintEntry({
            tokenId: 479,
            user: 0x68BDD37b9aD6Ef885e85237A075B104a50AfC1f1,
            mintAmount: 13614640593613910375,
            depositAmount: 41817034655093180000
        });
        entries[364] = MintEntry({
            tokenId: 481,
            user: 0x691c57e85b732dCC2Cfa126a7480Cb5f326E6bD1,
            mintAmount: 40801252399159013174,
            depositAmount: 96412244000000000000
        });
        entries[365] = MintEntry({
            tokenId: 483,
            user: 0x69aa6A0a9346669744895e6a48E45b1C5B1E7667,
            mintAmount: 205901552997551000178,
            depositAmount: 497500000000000000000
        });
        entries[366] = MintEntry({
            tokenId: 484,
            user: 0x69F1C41b58eE473c6789851b425599C45F03833e,
            mintAmount: 369619924025130658174,
            depositAmount: 969505192432867600000
        });
        entries[367] = MintEntry({
            tokenId: 485,
            user: 0x69f35FB0048A6EDBa6908a5B81BDb983ef3cD8e2,
            mintAmount: 79946217509988683990,
            depositAmount: 199000000000000000000
        });
        entries[368] = MintEntry({
            tokenId: 486,
            user: 0x6A61661c7DDAF0f4a45deE2B693059ca0909c643,
            mintAmount: 100954838815140960644,
            depositAmount: 237299890238149400000
        });
        entries[369] = MintEntry({
            tokenId: 487,
            user: 0x6a9d961e487F3AD2B0FcE2fbB6487Dc4b0FC9452,
            mintAmount: 71013215061651045826,
            depositAmount: 282512479713220850000
        });
        entries[370] = MintEntry({
            tokenId: 488,
            user: 0x6ab27D9a127C47F3f6c64C6472fe309332453d3a,
            mintAmount: 278482765339661693090,
            depositAmount: 667000000000000000000
        });
        entries[371] = MintEntry({
            tokenId: 489,
            user: 0x6accD26626c150a4b485E6c9c541b38FE0AB5915,
            mintAmount: 2259818468725565512500,
            depositAmount: 6148188372989876000000
        });
        entries[372] = MintEntry({
            tokenId: 490,
            user: 0x6aE1f0117D7ff74A49a869B1e7e5dd3c48864013,
            mintAmount: 89503847775432125614,
            depositAmount: 199936722723549350000
        });
        entries[373] = MintEntry({
            tokenId: 491,
            user: 0x6AF22DA734cd6acc11CA39d05E9654cf63bf5086,
            mintAmount: 9177020199273064448,
            depositAmount: 22029603825810800000
        });
        entries[374] = MintEntry({
            tokenId: 492,
            user: 0x6b3d1A37B5C01901341F01F4975D31bC5e6c3d81,
            mintAmount: 14455118226984264883,
            depositAmount: 46879954444140536000
        });
        entries[375] = MintEntry({
            tokenId: 495,
            user: 0x6bDF125600a7C4a0125B4735034573481d8BFCFB,
            mintAmount: 39826169094539946597,
            depositAmount: 96365316000000000000
        });
        entries[376] = MintEntry({
            tokenId: 496,
            user: 0x6BeDC20d252A1aE2371F250D569A6025Da0222bE,
            mintAmount: 51134665507690041338,
            depositAmount: 122374046047028920000
        });
        entries[377] = MintEntry({
            tokenId: 498,
            user: 0x6c10BFCd97611c671A23752E8E48bf5aF26049C3,
            mintAmount: 1203332503783446536563,
            depositAmount: 3901792026788122600000
        });
        entries[378] = MintEntry({
            tokenId: 499,
            user: 0x6c228F3F5Fe539f89e2267db26391928b36CA871,
            mintAmount: 95280040964425953771,
            depositAmount: 232107588175879270000
        });
        entries[379] = MintEntry({
            tokenId: 500,
            user: 0x6c3C301bB3AF46c86205844c7Ad9eF8bD6593BaF,
            mintAmount: 361461774577547358856,
            depositAmount: 947000000000000000000
        });
        entries[380] = MintEntry({
            tokenId: 501,
            user: 0x6CF8118892209d3975C9A03f06f7c11163BE2Ff8,
            mintAmount: 39386359174651599295,
            depositAmount: 99999920000000000000
        });
        entries[381] = MintEntry({
            tokenId: 503,
            user: 0x6dA7514cefB979de2D1D69519E97B4893Ab94cA0,
            mintAmount: 311432070073645089405,
            depositAmount: 749777780007975300000
        });
        entries[382] = MintEntry({
            tokenId: 504,
            user: 0x6da9AAa73D39F3880119Fd20e6d6a2f65Dd44ABe,
            mintAmount: 8492954741439498002,
            depositAmount: 20000000000000000000
        });
        entries[383] = MintEntry({
            tokenId: 505,
            user: 0x6eAba52965Fab0B404bebbDA594A2BA72Bdb6288,
            mintAmount: 31134864103062846358,
            depositAmount: 150000000000000000000
        });
        entries[384] = MintEntry({
            tokenId: 506,
            user: 0x6EFbC95c2E95EddF30e7009752Eb148ac885a1D4,
            mintAmount: 393605899414712456576,
            depositAmount: 984300000000000000000
        });
        entries[385] = MintEntry({
            tokenId: 507,
            user: 0x6f0B2dfFFAb5b4485BC6EBB9338760597310Afc1,
            mintAmount: 4910395187455672071,
            depositAmount: 10000000000000000000
        });
        entries[386] = MintEntry({
            tokenId: 510,
            user: 0x6F79f232ae4D34102b26F2948EDe2f858768fDD4,
            mintAmount: 2036965926714215883806,
            depositAmount: 4657451777800810000000
        });
        entries[387] = MintEntry({
            tokenId: 511,
            user: 0x6fe26B91BFb8Fd476Aa1cd4D6C0B325F0959631c,
            mintAmount: 1652457174666342299293,
            depositAmount: 3994433711520252000000
        });
        entries[388] = MintEntry({
            tokenId: 513,
            user: 0x70106ED6698306B17BeFdf7A45459e869EbFbBAB,
            mintAmount: 515963410710852646302,
            depositAmount: 1250000000000000000000
        });
        entries[389] = MintEntry({
            tokenId: 514,
            user: 0x70C09Ee6AE2b49c9Fe22254Ebdb1B224B8A75FCb,
            mintAmount: 468446661376275038495,
            depositAmount: 1091375929475144400000
        });
        entries[390] = MintEntry({
            tokenId: 516,
            user: 0x7118546B47427DBE0Bf6f2F414b067b83886A589,
            mintAmount: 167067000871966549925,
            depositAmount: 399645514430000000000
        });
        entries[391] = MintEntry({
            tokenId: 517,
            user: 0x714Cfc2bF843fceb605146E7C39f2B87eD0333CD,
            mintAmount: 48994652906468804899,
            depositAmount: 135900000000000000000
        });
        entries[392] = MintEntry({
            tokenId: 518,
            user: 0x7182ae7E0991b70e3Bf2c713658Dcdfb24ff12c7,
            mintAmount: 5779353211246983907506,
            depositAmount: 23004883394890000000000
        });
        entries[393] = MintEntry({
            tokenId: 519,
            user: 0x71aC7E6f6ADD5efED2C65D34d9474A6319769fb1,
            mintAmount: 63980249673757045937,
            depositAmount: 182940749630000000000
        });
        entries[394] = MintEntry({
            tokenId: 520,
            user: 0x71B095f10633f7aC65Cac6B476A3F0632339c5E4,
            mintAmount: 1276517406429360259666,
            depositAmount: 2974000000000000000000
        });
        entries[395] = MintEntry({
            tokenId: 521,
            user: 0x71c84272bAC17F19f0AE64a3B266e052E74fCE57,
            mintAmount: 327813437751799874638,
            depositAmount: 897153319932564000000
        });
        entries[396] = MintEntry({
            tokenId: 523,
            user: 0x7302858FE810f400fbA607E5DC844990302a5fdb,
            mintAmount: 39607390503237041800,
            depositAmount: 99542029977831160000
        });
        entries[397] = MintEntry({
            tokenId: 524,
            user: 0x73a7984C3379aEeDF004BC21bf2d614a2584b48F,
            mintAmount: 330499972165053962259,
            depositAmount: 769663761980000000000
        });
        entries[398] = MintEntry({
            tokenId: 525,
            user: 0x73AaECad12A5aE486caEe181F278DBb41a12b0f7,
            mintAmount: 57252798647219953576,
            depositAmount: 185706967830000000000
        });
        entries[399] = MintEntry({
            tokenId: 526,
            user: 0x73BD4982DA46E0BFC32442A226c248980071f3d3,
            mintAmount: 40856715706748267060,
            depositAmount: 97676880000000000000
        });
        entries[400] = MintEntry({
            tokenId: 528,
            user: 0x73D8C7ECEE8D879F433404A724Bfb6B467cb8C3D,
            mintAmount: 1344088540648204578964,
            depositAmount: 4976972000000000000000
        });
        entries[401] = MintEntry({
            tokenId: 529,
            user: 0x741151fA733C3360bbbF47A9A55a34fd1a0bA598,
            mintAmount: 65047056538159436021,
            depositAmount: 179940189208913700000
        });
        entries[402] = MintEntry({
            tokenId: 530,
            user: 0x742b6DE8Cb16327B68c83e1d6433174dB89FD2E0,
            mintAmount: 444496732875036110056,
            depositAmount: 1200000000000000000000
        });
        entries[403] = MintEntry({
            tokenId: 533,
            user: 0x75D27512Eb8Ca405f06934b251675f09E681Cf7E,
            mintAmount: 1899636536291499034156,
            depositAmount: 5781396859225553000000
        });
        entries[404] = MintEntry({
            tokenId: 534,
            user: 0x7601f59A937899D780a55b33f4fe4983178F63aF,
            mintAmount: 1421362698985253962672,
            depositAmount: 2999997331479472000000
        });
        entries[405] = MintEntry({
            tokenId: 535,
            user: 0x76046753bd15B8A3FcfaC367eFc9dC8f7194d62c,
            mintAmount: 2692735992448289362,
            depositAmount: 6343831548633650000
        });
        entries[406] = MintEntry({
            tokenId: 536,
            user: 0x7696DdCd0D660faEE2379d816A1f507Ec3175b76,
            mintAmount: 348415382151271182337,
            depositAmount: 845890060000000000000
        });
        entries[407] = MintEntry({
            tokenId: 537,
            user: 0x76D542089f923B08Da0B8174e0150cA2217566F9,
            mintAmount: 25202982080085941880,
            depositAmount: 60315069219082270000
        });
        entries[408] = MintEntry({
            tokenId: 540,
            user: 0x78217F41de80F18E96E3C1695A2Bcb96AdF64f7a,
            mintAmount: 833602756098733207217,
            depositAmount: 2194529213007096000000
        });
        entries[409] = MintEntry({
            tokenId: 541,
            user: 0x7821f46f652D5485d6E4FE3B66F30DA3351fc6f7,
            mintAmount: 1358769843508906775321,
            depositAmount: 3851923382988373500000
        });
        entries[410] = MintEntry({
            tokenId: 542,
            user: 0x78555E30Fdc1710405deFbE72a2Cd34279485a4B,
            mintAmount: 546997359190722731303,
            depositAmount: 1250000000000000000000
        });
        entries[411] = MintEntry({
            tokenId: 543,
            user: 0x787b4b7FFEf8edDaD54F311039aCF4c36FEC9593,
            mintAmount: 3952724899018674465379,
            depositAmount: 14957779999853111000000
        });
        entries[412] = MintEntry({
            tokenId: 544,
            user: 0x7884c05101ADE3aCa9631D21282a47a25868955F,
            mintAmount: 60495165403678390129,
            depositAmount: 149999800950419980000
        });
        entries[413] = MintEntry({
            tokenId: 545,
            user: 0x789645A3C66E8988973DC32a52740d017b1EF807,
            mintAmount: 4409505627913880399,
            depositAmount: 11005391285155625000
        });
        entries[414] = MintEntry({
            tokenId: 547,
            user: 0x78BD86640Dd12FdbDa74749d817da7A0Dda02e68,
            mintAmount: 66961689093440132491,
            depositAmount: 180000000000000000000
        });
        entries[415] = MintEntry({
            tokenId: 548,
            user: 0x78e454A89D661372a8455D44D0e5185f8f057287,
            mintAmount: 1447459831319051983281,
            depositAmount: 3992909629324064700000
        });
        entries[416] = MintEntry({
            tokenId: 549,
            user: 0x78ebCDa5a906EB9328863a890397c93f8C840898,
            mintAmount: 87475020721925033786,
            depositAmount: 250000000000000000000
        });
        entries[417] = MintEntry({
            tokenId: 550,
            user: 0x79230bb65942D075C5E9496277DB39DA175a5B71,
            mintAmount: 17457298184232320848686,
            depositAmount: 50000000000000000000000
        });
        entries[418] = MintEntry({
            tokenId: 551,
            user: 0x794A0BA3689ba74daE8bcF0E395F4811574989cf,
            mintAmount: 337482576245318996604,
            depositAmount: 782766923440000000000
        });
        entries[419] = MintEntry({
            tokenId: 552,
            user: 0x79506ca291aF8e85b39E59766762C35ae18248b3,
            mintAmount: 417976155025814905876,
            depositAmount: 970708963140000000000
        });
        entries[420] = MintEntry({
            tokenId: 553,
            user: 0x796AF567a13526dDeE9db783DE07c833f0183860,
            mintAmount: 1021115607516027422748,
            depositAmount: 2474902396685621700000
        });
        entries[421] = MintEntry({
            tokenId: 554,
            user: 0x7971DDe7bE09d03d319F77a1251bed9Ffa4c72d5,
            mintAmount: 339295607089827063526,
            depositAmount: 917256142128493800000
        });
        entries[422] = MintEntry({
            tokenId: 555,
            user: 0x79882B16121a4e8019e3f4075aA466988205CcF5,
            mintAmount: 1062333752828737775268,
            depositAmount: 2475000000000000000000
        });
        entries[423] = MintEntry({
            tokenId: 556,
            user: 0x798a0f86E2e267130b814361C0853640aF4E629A,
            mintAmount: 45247261795836476259,
            depositAmount: 111572372643276910000
        });
        entries[424] = MintEntry({
            tokenId: 558,
            user: 0x79dE94216395eAFe072B8B50216b5648eDb3f609,
            mintAmount: 108796360947570187506,
            depositAmount: 266623766603519200000
        });
        entries[425] = MintEntry({
            tokenId: 560,
            user: 0x79f08F2e75A8C99428DE4A2e6456c07C99E55da5,
            mintAmount: 99072372484914857565083,
            depositAmount: 199959804715446670000000
        });
        entries[426] = MintEntry({
            tokenId: 561,
            user: 0x7a0dff2a955B72159650300a9aCeF97146dd12e6,
            mintAmount: 3720916388093229871,
            depositAmount: 10000000000000000000
        });
        entries[427] = MintEntry({
            tokenId: 563,
            user: 0x7af17725d3b001c522DD5Fc18829292f47c75B2C,
            mintAmount: 969568016301086899792,
            depositAmount: 2128290418653674000000
        });
        entries[428] = MintEntry({
            tokenId: 564,
            user: 0x7B77bE2599c9a6b544514c1E0B7CcA70704EF4fc,
            mintAmount: 522632027922576805100,
            depositAmount: 1204678354769464500000
        });
        entries[429] = MintEntry({
            tokenId: 567,
            user: 0x7bEAcbFE7B7655EAace6355E776762bA1F54Ab65,
            mintAmount: 141286430655551078781,
            depositAmount: 340000000000000000000
        });
        entries[430] = MintEntry({
            tokenId: 568,
            user: 0x7bfc6a37Ce167F620ba13F3dDAf426C3e25C8933,
            mintAmount: 86727047828728036580,
            depositAmount: 207765910960000000000
        });
        entries[431] = MintEntry({
            tokenId: 570,
            user: 0x7c8477e426489f8a08a2B2f478f34E4110a10212,
            mintAmount: 59582727839877395845,
            depositAmount: 149000000000000000000
        });
        entries[432] = MintEntry({
            tokenId: 571,
            user: 0x7Cba874CA2Db825cfE34079664c12562350F1927,
            mintAmount: 73072071488065949506,
            depositAmount: 209460765562159300000
        });
        entries[433] = MintEntry({
            tokenId: 572,
            user: 0x7d52B2B2aEdA25a2ACdabBc74bd9E2C30B4D36D7,
            mintAmount: 1784548270343760531472,
            depositAmount: 3598749131135880000000
        });
        entries[434] = MintEntry({
            tokenId: 573,
            user: 0x7dAc878B074eE54482a9E6CE46CC8f1a965DCa84,
            mintAmount: 427639044442799800046,
            depositAmount: 1000000000000000000000
        });
        entries[435] = MintEntry({
            tokenId: 574,
            user: 0x7dE31dC0aC10e263491F7123b140F9CbF860d2a8,
            mintAmount: 35854022709070989260,
            depositAmount: 100000000000000000000
        });
        entries[436] = MintEntry({
            tokenId: 575,
            user: 0x7dF2cCfc4f5e025e424092A1C148c883A39301ec,
            mintAmount: 6266727343762325815,
            depositAmount: 14962235828622550000
        });
        entries[437] = MintEntry({
            tokenId: 577,
            user: 0x7e4067FD59Cd1083560001f17BAF8B8Bd77128a1,
            mintAmount: 2574569196545467260161,
            depositAmount: 5185921963678857000000
        });
        entries[438] = MintEntry({
            tokenId: 578,
            user: 0x7E6E79C47aDA76E8FB0Ac246E3450Be9844E71fF,
            mintAmount: 31268054078486503141,
            depositAmount: 107198993016417520000
        });
        entries[439] = MintEntry({
            tokenId: 579,
            user: 0x7E8637430f9CEcc4B893bf4787e399325aa23A93,
            mintAmount: 26303147289722468579,
            depositAmount: 57238660000000000000
        });
        entries[440] = MintEntry({
            tokenId: 580,
            user: 0x7E949d18a816B0c57876818C49093996b1B5D4F1,
            mintAmount: 1655401001162151038497,
            depositAmount: 4270444755579414000000
        });
        entries[441] = MintEntry({
            tokenId: 581,
            user: 0x7F8532f1108e31a3FF5B0dF446Ba96ca99611932,
            mintAmount: 2509275790413923080,
            depositAmount: 79780975383163290000
        });
        entries[442] = MintEntry({
            tokenId: 582,
            user: 0x7F9eb6e1bAE5565cA4a23c5fA3108b64Abe9A707,
            mintAmount: 933802193991375692898,
            depositAmount: 2319646389933486400000
        });
        entries[443] = MintEntry({
            tokenId: 583,
            user: 0x7fBa36C647cC537A6e08bd981Cd8deE6727b0f4F,
            mintAmount: 2853694988159783644920,
            depositAmount: 9152992649771536000000
        });
        entries[444] = MintEntry({
            tokenId: 584,
            user: 0x80106198DC662f5E02E79dE2BE10052e5aE016C2,
            mintAmount: 18564138258930271296,
            depositAmount: 49999973949940010000
        });
        entries[445] = MintEntry({
            tokenId: 587,
            user: 0x80952412dbb39a48092436EFd17c23A46fF0D987,
            mintAmount: 3463561126782141098544,
            depositAmount: 10000000000000000000000
        });
        entries[446] = MintEntry({
            tokenId: 588,
            user: 0x80a7BB293627bC726A7AE3Bed35A2057F5be74Fe,
            mintAmount: 469843641109221583636,
            depositAmount: 1140010053526867800000
        });
        entries[447] = MintEntry({
            tokenId: 589,
            user: 0x80E4930b1cee159d6BDCbC0F8490D0A3f2AAb51E,
            mintAmount: 827612630254611331801,
            depositAmount: 2020414512700738500000
        });
        entries[448] = MintEntry({
            tokenId: 590,
            user: 0x80F609aDfCEB731e8E620963bd194F4DB9f56cC1,
            mintAmount: 23291838258388395049,
            depositAmount: 61093995926690480000
        });
        entries[449] = MintEntry({
            tokenId: 591,
            user: 0x814d2dCC371257a878bE75462c572274Ac2ae7b4,
            mintAmount: 8938916032873222303704,
            depositAmount: 30000000000000000000000
        });
        entries[450] = MintEntry({
            tokenId: 592,
            user: 0x81ad112bf6e0E310fEEfca553C82FcA1Ed90A538,
            mintAmount: 1326428623098341876777,
            depositAmount: 4500751356612817000000
        });
        entries[451] = MintEntry({
            tokenId: 594,
            user: 0x826907545C05eeB57afE3f4B3f1eCbAf16f80F2C,
            mintAmount: 76312090309492119045,
            depositAmount: 183380000000000000000
        });
        entries[452] = MintEntry({
            tokenId: 596,
            user: 0x82e15016CF7E33a7EA98E9bC41887ec086076495,
            mintAmount: 273897169677390728490,
            depositAmount: 1000000000000000000000
        });
        entries[453] = MintEntry({
            tokenId: 597,
            user: 0x83aB8e31df35AA3281d630529C6F4bf5AC7f7aBF,
            mintAmount: 929560238643390729201,
            depositAmount: 2687567435341348500000
        });
        entries[454] = MintEntry({
            tokenId: 598,
            user: 0x8443e25075C301C808F359fB0F157Bc340BfC7cE,
            mintAmount: 253053381764578782389,
            depositAmount: 565048853890000000000
        });
        entries[455] = MintEntry({
            tokenId: 599,
            user: 0x845B84d629668280E1aAa3935756efE89b2Fe268,
            mintAmount: 187998599142140196974,
            depositAmount: 448646742825695900000
        });
        entries[456] = MintEntry({
            tokenId: 600,
            user: 0x84a983125C6a48e51CFd1BfDE8952C3D47fF4e98,
            mintAmount: 46450375297148202303,
            depositAmount: 121055831051782140000
        });
        entries[457] = MintEntry({
            tokenId: 602,
            user: 0x84C42a0F1DFf1bb673BCCd63bCa73e672225EDA2,
            mintAmount: 553204154836521771403,
            depositAmount: 1330173075679969800000
        });
        entries[458] = MintEntry({
            tokenId: 603,
            user: 0x851839E750845933929bfAf2BFFF259f2D37D3E0,
            mintAmount: 99572369242544375654,
            depositAmount: 252790531020636230000
        });
        entries[459] = MintEntry({
            tokenId: 604,
            user: 0x852639CD40464B5C99E3999eD00260EeA2e3ddeF,
            mintAmount: 439085070967690669582,
            depositAmount: 983859486046446400000
        });
        entries[460] = MintEntry({
            tokenId: 605,
            user: 0x855dD67818F6A7942f4F159c198Fc1EcA7803B14,
            mintAmount: 1864787825986351544969,
            depositAmount: 4228794812538408700000
        });
        entries[461] = MintEntry({
            tokenId: 606,
            user: 0x858cDC330dF0af12418e1ECC232c37551E5cb3D7,
            mintAmount: 61862630605471700035,
            depositAmount: 147766040210338050000
        });
        entries[462] = MintEntry({
            tokenId: 607,
            user: 0x85de5648e1c4c42b0CC6b056B17C1bCeE3ed5957,
            mintAmount: 11482130776337768912,
            depositAmount: 30258586556209470000
        });
        entries[463] = MintEntry({
            tokenId: 608,
            user: 0x85Eb872c4274Df8b9e596B3BBa490B205D79122E,
            mintAmount: 215087801284677097646,
            depositAmount: 493000000000000000000
        });
        entries[464] = MintEntry({
            tokenId: 610,
            user: 0x86985654e56458153D103245df90532FA4234728,
            mintAmount: 422993734997741655482,
            depositAmount: 999378770525062800000
        });
        entries[465] = MintEntry({
            tokenId: 611,
            user: 0x86eBbA6FA5b00610496b1b6bcA8EBF789ee91679,
            mintAmount: 747212405227165553823,
            depositAmount: 2020825168000000000000
        });
        entries[466] = MintEntry({
            tokenId: 615,
            user: 0x8873E590a918B4B72517c84c7F9E6201C79A1ace,
            mintAmount: 3357688737856720666,
            depositAmount: 9085304845927740000
        });
        entries[467] = MintEntry({
            tokenId: 616,
            user: 0x889FD4C5ab0D00b23ED4fB32ab2F9FA2c38bE4d4,
            mintAmount: 31461244239193196080,
            depositAmount: 68232919884101360000
        });
        entries[468] = MintEntry({
            tokenId: 618,
            user: 0x88Fc3F3B865A015C5b63572716a534325bA8be6d,
            mintAmount: 1131166716152728284619,
            depositAmount: 2977891310000000000000
        });
        entries[469] = MintEntry({
            tokenId: 619,
            user: 0x890ab4cb5111BEA4Dd325B3A5A7eFD02Ef8af7f8,
            mintAmount: 34202746424300901033,
            depositAmount: 83433900606843360000
        });
        entries[470] = MintEntry({
            tokenId: 620,
            user: 0x8928E65d16533DD6452Cc7623eA63a0a8CEB7534,
            mintAmount: 79821129867567725847,
            depositAmount: 193464387539781300000
        });
        entries[471] = MintEntry({
            tokenId: 621,
            user: 0x8934d2c764570b0A9C0DFFdD7C376Db06f957fA7,
            mintAmount: 237845158819693943635,
            depositAmount: 600000000000000000000
        });
        entries[472] = MintEntry({
            tokenId: 622,
            user: 0x893b8De270e654ede36266d3a228cF41b4E9a4f5,
            mintAmount: 3650573050486557413866,
            depositAmount: 11440126051546565000000
        });
        entries[473] = MintEntry({
            tokenId: 624,
            user: 0x89688542873276Cd7d9Cea936b25F37778a593fd,
            mintAmount: 210402420698777121334,
            depositAmount: 499406813310078400000
        });
        entries[474] = MintEntry({
            tokenId: 628,
            user: 0x89a6Ed7e49E86efa418b6Fd5970D47fe88A27FE4,
            mintAmount: 3264247867072396427548,
            depositAmount: 7984969632200000000000
        });
        entries[475] = MintEntry({
            tokenId: 630,
            user: 0x8ac8D1007D9350BeB4272D20D66B1EFC574d95A4,
            mintAmount: 194008831396028807451,
            depositAmount: 500485378460944600000
        });
        entries[476] = MintEntry({
            tokenId: 631,
            user: 0x8aeF943D5A12e77443C14C65412fbF7024274BF8,
            mintAmount: 191233284487427820797,
            depositAmount: 465648123390000000000
        });
        entries[477] = MintEntry({
            tokenId: 632,
            user: 0x8B07Ff11BCCED60470bbA18F8C798B2a149e6B06,
            mintAmount: 11018465272858799577,
            depositAmount: 28822730065958138000
        });
        entries[478] = MintEntry({
            tokenId: 634,
            user: 0x8b87E652922445BCaC00887e637A07A31af47B02,
            mintAmount: 356276919250537016047,
            depositAmount: 800000000000000000000
        });
        entries[479] = MintEntry({
            tokenId: 635,
            user: 0x8C126eB5aDA6C61f5B48e9791d5D539576aF87Cb,
            mintAmount: 162640520477222041990,
            depositAmount: 389226727981605400000
        });
        entries[480] = MintEntry({
            tokenId: 636,
            user: 0x8c196a92F073f30b96d3D0ce6C1e8eF9BB456C2b,
            mintAmount: 152614416154305289853,
            depositAmount: 367893225523011200000
        });
        entries[481] = MintEntry({
            tokenId: 637,
            user: 0x8c5cf166A8ACf5E5F1F3c8E68440f66693e23D58,
            mintAmount: 2087284459607680656,
            depositAmount: 5000000000000000000
        });
        entries[482] = MintEntry({
            tokenId: 638,
            user: 0x8cb4CBb1CC9488d55F97898D92A9aCbf84A33bA1,
            mintAmount: 69032026792203884057,
            depositAmount: 149420982037500000000
        });
        entries[483] = MintEntry({
            tokenId: 639,
            user: 0x8cFd67a067431A339b78c2C7e9b3E5675651460e,
            mintAmount: 228472923152176739227,
            depositAmount: 543696482720000000000
        });
        entries[484] = MintEntry({
            tokenId: 640,
            user: 0x8D370E8529AFbbdfCd184F749D30cBa98754a785,
            mintAmount: 275040408190761320336,
            depositAmount: 1000000000000000000000
        });
        entries[485] = MintEntry({
            tokenId: 641,
            user: 0x8d452c1f4bAE385B13933c83EcFf70D74229915F,
            mintAmount: 485077280366499288,
            depositAmount: 1072332788522388700
        });
        entries[486] = MintEntry({
            tokenId: 642,
            user: 0x8d605e606b3AEe143ff0d039F63100a52F17d85F,
            mintAmount: 41909206444524881124349,
            depositAmount: 84901367539550750000000
        });
        entries[487] = MintEntry({
            tokenId: 643,
            user: 0x8D8CC393220DA84a53667E48c25e767499DCE4fB,
            mintAmount: 21289697305256707896,
            depositAmount: 46147545644924780000
        });
        entries[488] = MintEntry({
            tokenId: 645,
            user: 0x8E430677DdFe39cCFbdB6E264b7B1393565A79dE,
            mintAmount: 7378750895064698197895,
            depositAmount: 26551285938592684000000
        });
        entries[489] = MintEntry({
            tokenId: 646,
            user: 0x8e4C8C0fbA7806EBd7b808fd5D47bB9EDAA21f83,
            mintAmount: 2000150292424523003075,
            depositAmount: 5796039446439984000000
        });
        entries[490] = MintEntry({
            tokenId: 647,
            user: 0x8e8741aB54Ba496D415dda932ce73d5dec65Ff86,
            mintAmount: 83607594650597891211,
            depositAmount: 200000000000000000000
        });
        entries[491] = MintEntry({
            tokenId: 648,
            user: 0x8EB2E0cebcD191625037a042C9edF67b7F7FD74C,
            mintAmount: 142236805322112802840921,
            depositAmount: 399537080286037600000000
        });
        entries[492] = MintEntry({
            tokenId: 649,
            user: 0x8f73BCdea6D513023f438913F93e43D60Ab7a715,
            mintAmount: 461203339159160587695,
            depositAmount: 1198764074230000000000
        });
        entries[493] = MintEntry({
            tokenId: 653,
            user: 0x90465281FaF8f8dEcE4f71c3F4B9Df9DCc13Ca57,
            mintAmount: 1214024877008602399033,
            depositAmount: 2868294701760000000000
        });
        entries[494] = MintEntry({
            tokenId: 654,
            user: 0x904b8f6D1162B6C3a91B721301B4231f04195d36,
            mintAmount: 1520922917775286537232,
            depositAmount: 3638162027670000000000
        });
        entries[495] = MintEntry({
            tokenId: 656,
            user: 0x90859216cFA0A4F99df9Ad561778Fe726181619C,
            mintAmount: 148164935716661150144,
            depositAmount: 487388638090000000000
        });
        entries[496] = MintEntry({
            tokenId: 657,
            user: 0x90a1d987261f095bB7Fff1e4AC4D059c263Bc8C1,
            mintAmount: 74689874966064963146,
            depositAmount: 242922386300000000000
        });
        entries[497] = MintEntry({
            tokenId: 658,
            user: 0x910fc35d33e0875a5942eADaE02ede7C430f1440,
            mintAmount: 41216814190718778937,
            depositAmount: 98254600000000000000
        });
        entries[498] = MintEntry({
            tokenId: 659,
            user: 0x9160062121840C5356E9b02a528d7F8a53b2EB02,
            mintAmount: 1100090452132198163436,
            depositAmount: 2451607698840000000000
        });
        entries[499] = MintEntry({
            tokenId: 660,
            user: 0x917a08b06d78390B73e121166D547381A662F98C,
            mintAmount: 42262102812715446239,
            depositAmount: 99691310439608350000
        });
        entries[500] = MintEntry({
            tokenId: 661,
            user: 0x926A4f20fde399A7E621bD6Bc613D3D0B20BC486,
            mintAmount: 1159639059472599092895,
            depositAmount: 2359710358566940700000
        });
        entries[501] = MintEntry({
            tokenId: 662,
            user: 0x936D5A50793a34ae1884aAa6432469E72D4CAc6c,
            mintAmount: 599260971625325949547,
            depositAmount: 1630000000000000000000
        });
        entries[502] = MintEntry({
            tokenId: 664,
            user: 0x9389d9e95F8D409b1E6CA7085F0aDa92E546eE5f,
            mintAmount: 716653313364843450628,
            depositAmount: 1669592704376272000000
        });
        entries[503] = MintEntry({
            tokenId: 666,
            user: 0x94443480DDe03F5199C9AADbADd0171d4d9C96b7,
            mintAmount: 396706740642190598293,
            depositAmount: 1150462238230766800000
        });
        entries[504] = MintEntry({
            tokenId: 667,
            user: 0x945a5dbc95fDD6c0Aa873ACfc0d3CD4888E28E61,
            mintAmount: 498512462335745522716,
            depositAmount: 1618357772599255600000
        });
        entries[505] = MintEntry({
            tokenId: 668,
            user: 0x945d5bcda8dCd9Cd8b221fd23CF4b6C0E7e50bD5,
            mintAmount: 369651662328528307579,
            depositAmount: 880746358110000000000
        });
        entries[506] = MintEntry({
            tokenId: 669,
            user: 0x94c02fa483EC1670141e2e3dec79AB6087bCb836,
            mintAmount: 81174794332119291913,
            depositAmount: 196872140000000000000
        });
        entries[507] = MintEntry({
            tokenId: 672,
            user: 0x9568f8c0557bEdFbb546D33c6ac5388e2342aC56,
            mintAmount: 1144239827245418420,
            depositAmount: 2292964307415579600
        });
        entries[508] = MintEntry({
            tokenId: 673,
            user: 0x9571F1Bac623CbA1e39b45e81DC2436F30BF9Edf,
            mintAmount: 57293975141951396984,
            depositAmount: 136295076386682680000
        });
        entries[509] = MintEntry({
            tokenId: 674,
            user: 0x957Ee7a79Cead5337746a468ece63C23bEf8bd4f,
            mintAmount: 183771806871083423027,
            depositAmount: 500000000000000000000
        });
        entries[510] = MintEntry({
            tokenId: 675,
            user: 0x9586B4D096Afa1744C16eB3a587237d3a5ca35a6,
            mintAmount: 37433167451951051626,
            depositAmount: 98545954782046490000
        });
        entries[511] = MintEntry({
            tokenId: 676,
            user: 0x9603B58cbb72A0943b422dA5F78d12cEAe0d9dc9,
            mintAmount: 46109712455962077640,
            depositAmount: 110489100000000000000
        });
        entries[512] = MintEntry({
            tokenId: 677,
            user: 0x9667d7e702B28617918697fd9789B07F563d2a52,
            mintAmount: 7178839446021703745519,
            depositAmount: 16187908505768090000000
        });
        entries[513] = MintEntry({
            tokenId: 678,
            user: 0x97008Bf239Ff30cFE34E51627EFD538740278529,
            mintAmount: 416617906596717086054,
            depositAmount: 1000000000000000000000
        });
        entries[514] = MintEntry({
            tokenId: 679,
            user: 0x9734dF024C332b631dc113ee86419e5108ead54e,
            mintAmount: 41078404278458405193247,
            depositAmount: 82156808556916800000000
        });
        entries[515] = MintEntry({
            tokenId: 680,
            user: 0x976e7bE658529e14bBE566758BfAC68f7A06Cf93,
            mintAmount: 101164467150550492884,
            depositAmount: 253169758647319300000
        });
        entries[516] = MintEntry({
            tokenId: 681,
            user: 0x979678A3C2e3d3912164bD12D185ab427Ce3a7a6,
            mintAmount: 108809517033688518520,
            depositAmount: 307019860172569800000
        });
        entries[517] = MintEntry({
            tokenId: 682,
            user: 0x97Da894D59E966f017eA171D9a2669F6FA7EA921,
            mintAmount: 67445328376173872679,
            depositAmount: 269378046143546700000
        });
        entries[518] = MintEntry({
            tokenId: 683,
            user: 0x981E27C556Eb4ACa03f2f5b97b2810DDDd4EB136,
            mintAmount: 9574041916407142912,
            depositAmount: 22944235238208060000
        });
        entries[519] = MintEntry({
            tokenId: 684,
            user: 0x984A62119aad363Fc78C049279Cfd688D978B7D5,
            mintAmount: 74449407473193102891,
            depositAmount: 227772062920000000000
        });
        entries[520] = MintEntry({
            tokenId: 685,
            user: 0x98E23D501615b649c9C9b6B375a8158960AE835b,
            mintAmount: 62938966761737992688,
            depositAmount: 170404498450910000000
        });
        entries[521] = MintEntry({
            tokenId: 686,
            user: 0x98FFe254ED8E7fA5ad716678aa196622dB36BD08,
            mintAmount: 4028947282473988860280,
            depositAmount: 13000000000000000000000
        });
        entries[522] = MintEntry({
            tokenId: 687,
            user: 0x990107ACFFd10Cc505634Fe4504a3B9b8DBC6fC7,
            mintAmount: 50502617322486780906,
            depositAmount: 119129711169837120000
        });
        entries[523] = MintEntry({
            tokenId: 688,
            user: 0x99496a4C0426e3dC0Eeda7F28298774DbeCF815a,
            mintAmount: 76210067524614681891,
            depositAmount: 223726668078565230000
        });
        entries[524] = MintEntry({
            tokenId: 689,
            user: 0x9957dc79309F95cc272D7dA1eE195Ae5865b9aAD,
            mintAmount: 304747721850498503334,
            depositAmount: 727925141240051100000
        });
        entries[525] = MintEntry({
            tokenId: 691,
            user: 0x99e86304A71df6E3181D4dC594E9da2c7B91E72d,
            mintAmount: 662058744534589886489,
            depositAmount: 1593680433803527700000
        });
        entries[526] = MintEntry({
            tokenId: 692,
            user: 0x99F38239cED2adE74695596E67D99809bE245653,
            mintAmount: 174623165009363615799,
            depositAmount: 380000000000000000000
        });
        entries[527] = MintEntry({
            tokenId: 693,
            user: 0x9a78cb2116C0979C44917444756185b65478b2F5,
            mintAmount: 396596897442651543454,
            depositAmount: 890901343886035500000
        });
        entries[528] = MintEntry({
            tokenId: 694,
            user: 0x9AD4a47E223312B4d8B15D514BD1f7Fb7Ee6AB8b,
            mintAmount: 617946241870058005,
            depositAmount: 1421391856811937300
        });
        entries[529] = MintEntry({
            tokenId: 695,
            user: 0x9B01a9Afec204c0815fFC78840872203Cd2f1282,
            mintAmount: 459534644761484831050,
            depositAmount: 1000000000000000000000
        });
        entries[530] = MintEntry({
            tokenId: 696,
            user: 0x9b0580Ad8e237d3DB62129Ea14383c0BeC3BEebe,
            mintAmount: 417074650961620730693,
            depositAmount: 993000000000000000000
        });
        entries[531] = MintEntry({
            tokenId: 698,
            user: 0x9bE8EE7700Bff356Ed169E3A50DCD58C2c20b9a6,
            mintAmount: 86632387254489274168,
            depositAmount: 180274470345000000000
        });
        entries[532] = MintEntry({
            tokenId: 700,
            user: 0x9c6DbE28Fc1a2CCdA153D2b74825f51874E54dF8,
            mintAmount: 401579544160733604960,
            depositAmount: 1085100000000000000000
        });
        entries[533] = MintEntry({
            tokenId: 701,
            user: 0x9C6E1c1ad7C94EE449177FAeBceC5d3894f5D940,
            mintAmount: 174068933070149651718,
            depositAmount: 414953793180000000000
        });
        entries[534] = MintEntry({
            tokenId: 703,
            user: 0x9C7Af0A3FedCAf7894E26BD1cF9C5ED0538a33DC,
            mintAmount: 458652898625611244556,
            depositAmount: 1047336707536249200000
        });
        entries[535] = MintEntry({
            tokenId: 704,
            user: 0x9cc4c01b7ce68111C590C5abEc58588aE196B712,
            mintAmount: 847391192784146170440,
            depositAmount: 2596924498189994700000
        });
        entries[536] = MintEntry({
            tokenId: 705,
            user: 0x9cC57A8a2196F1a6f517AdaB225EFee1D317c667,
            mintAmount: 3495330521446682337056,
            depositAmount: 9946918640190000000000
        });
        entries[537] = MintEntry({
            tokenId: 707,
            user: 0x9D1b700B525dee6aa63942C621348fdf4a2a822F,
            mintAmount: 43093264625663133868,
            depositAmount: 101718872233871180000
        });
        entries[538] = MintEntry({
            tokenId: 709,
            user: 0x9D27a13Fa20A2AD1d053a7741A6b5bFA658426a0,
            mintAmount: 5616947517613511390,
            depositAmount: 18552728000000000000
        });
        entries[539] = MintEntry({
            tokenId: 711,
            user: 0x9DD12C3Bc3e6037adFf76Ca9E900458446096426,
            mintAmount: 46590733034913484106,
            depositAmount: 100000000000000000000
        });
        entries[540] = MintEntry({
            tokenId: 712,
            user: 0x9e84bDb7456B75480bAb3E2D529C42836BE3E407,
            mintAmount: 6729376658509788159,
            depositAmount: 13480737194722380000
        });
        entries[541] = MintEntry({
            tokenId: 713,
            user: 0x9E8c2EC1CA2464ab49656708d4955Fd01B8464Ec,
            mintAmount: 61805270814600149542,
            depositAmount: 147500000000000000000
        });
        entries[542] = MintEntry({
            tokenId: 714,
            user: 0x9E9CC99A89aa7B73297e75Cf79F455090b07F586,
            mintAmount: 7427086067909215680654,
            depositAmount: 14985884153549351000000
        });
        entries[543] = MintEntry({
            tokenId: 715,
            user: 0x9eBFa326964A92274ab42B644860Ed9c051aFcf4,
            mintAmount: 10172543319775957123,
            depositAmount: 24378546588543530000
        });
        entries[544] = MintEntry({
            tokenId: 716,
            user: 0x9ee17841f2ad9E0D9Db095D81f56b98c7c1fAfCc,
            mintAmount: 7391476708208329327,
            depositAmount: 17519868478682670000
        });
        entries[545] = MintEntry({
            tokenId: 717,
            user: 0x9F26bda279D9bB5B590cB5F34A6716164680E26b,
            mintAmount: 1955045554562361251013,
            depositAmount: 4975500000000000000000
        });
        entries[546] = MintEntry({
            tokenId: 718,
            user: 0x9f431A46149bab70373B9C6867d2dB8C2F45aa11,
            mintAmount: 1417977088005952381304,
            depositAmount: 3398434107922005000000
        });
        entries[547] = MintEntry({
            tokenId: 719,
            user: 0x9ff47850F80BA1E6dC04141cB4C87243DcBc02E5,
            mintAmount: 247789800183135755345,
            depositAmount: 584640000000000000000
        });
        entries[548] = MintEntry({
            tokenId: 720,
            user: 0xA0076FF779911Be8136033049c6588f91F0BF447,
            mintAmount: 41262198628806589394,
            depositAmount: 99917368330000000000
        });
        entries[549] = MintEntry({
            tokenId: 721,
            user: 0xa01255f709599cf00676E874ae598d00D9E0694A,
            mintAmount: 41519543241073434857,
            depositAmount: 111608860000000000000
        });
        entries[550] = MintEntry({
            tokenId: 722,
            user: 0xa0516B264604099FDA522B0ec6ea1412511F2230,
            mintAmount: 18282093388484933194,
            depositAmount: 50225448148090760000
        });
        entries[551] = MintEntry({
            tokenId: 723,
            user: 0xa05c2cBf1bD87aFF96c42d2f7B735E29427833C1,
            mintAmount: 28884739988461272435,
            depositAmount: 69811407780000000000
        });
        entries[552] = MintEntry({
            tokenId: 724,
            user: 0xA0AdCA7465D8632937491B0Fd747C96B977952f5,
            mintAmount: 1539856048145837258032,
            depositAmount: 4462191356456426500000
        });
        entries[553] = MintEntry({
            tokenId: 725,
            user: 0xa0CD2aa0dAd8c5a1B8C9F0549A9D042b7F9a9578,
            mintAmount: 812891168522188548437,
            depositAmount: 2205538070760172000000
        });
        entries[554] = MintEntry({
            tokenId: 726,
            user: 0xa10D31B628bF5f9Fc8e02e91a7564Bb2a1E5Fea0,
            mintAmount: 29062069562058936631,
            depositAmount: 98747320727378440000
        });
        entries[555] = MintEntry({
            tokenId: 727,
            user: 0xa12358e39c9cA9d190a5c60130a64c06211bCcBa,
            mintAmount: 2823580048866350684501,
            depositAmount: 7426237900253796000000
        });
        entries[556] = MintEntry({
            tokenId: 728,
            user: 0xa12A918aa308dc665BdF54DfDee3840157354177,
            mintAmount: 1960682290374967137,
            depositAmount: 8000000000000000000
        });
        entries[557] = MintEntry({
            tokenId: 729,
            user: 0xa21d57703ec5238b4CbaDc6f1111AE1446b7d303,
            mintAmount: 229477296718200871831,
            depositAmount: 569783390000000000000
        });
        entries[558] = MintEntry({
            tokenId: 730,
            user: 0xa24194558FED443fD4AFd3637f04ebCdD5Cc41c5,
            mintAmount: 88730811447604633230,
            depositAmount: 237315391350000000000
        });
        entries[559] = MintEntry({
            tokenId: 731,
            user: 0xa25547A556439213176f9FECec50acc863305f59,
            mintAmount: 124099020122580666815,
            depositAmount: 300000000000000000000
        });
        entries[560] = MintEntry({
            tokenId: 732,
            user: 0xA258c204ECF349bDA77860Cb75FE0dFfF7Ec23e2,
            mintAmount: 57709854975683708008,
            depositAmount: 150000000000000000000
        });
        entries[561] = MintEntry({
            tokenId: 733,
            user: 0xa26A5F46Df8Ef6918F5c68D69DB9bC8ebb41AC03,
            mintAmount: 2106023082166403607919,
            depositAmount: 5281748911340000000000
        });
        entries[562] = MintEntry({
            tokenId: 735,
            user: 0xa2E83a7620dc31cA47Eb21dB08ee8cbdC48e1B55,
            mintAmount: 5869487285168227610317,
            depositAmount: 14936703504908038000000
        });
        entries[563] = MintEntry({
            tokenId: 736,
            user: 0xa30E54Cb3593c6afCA653621C4D3Ee2105F015aa,
            mintAmount: 1313379480395627185581,
            depositAmount: 3532233737283978700000
        });
        entries[564] = MintEntry({
            tokenId: 738,
            user: 0xa36eB34488dc2f4af3dbC3C0913E82569054e068,
            mintAmount: 7889337951626708580855,
            depositAmount: 22338725259180200000000
        });
        entries[565] = MintEntry({
            tokenId: 739,
            user: 0xa36F2F6E3Ccb90dED3024905037C2bF391b6438F,
            mintAmount: 40041280321170274506,
            depositAmount: 95000000000000000000
        });
        entries[566] = MintEntry({
            tokenId: 741,
            user: 0xA3b3D0DCfF250151Ba33C10C6660d0E651CDC501,
            mintAmount: 923384651850627647,
            depositAmount: 2097630842651446300
        });
        entries[567] = MintEntry({
            tokenId: 743,
            user: 0xa4b9213780C8ce6118cdCe6cdd7Bd003a73524BE,
            mintAmount: 19301856941257665307,
            depositAmount: 40000000000000000000
        });
        entries[568] = MintEntry({
            tokenId: 746,
            user: 0xA53b212A6e6f83B994ebf9cE5fDD71B80C55F258,
            mintAmount: 423591322018411089390,
            depositAmount: 1024000000000000000000
        });
        entries[569] = MintEntry({
            tokenId: 747,
            user: 0xA570F2bC2295532Ae260a59989Ec78692C715402,
            mintAmount: 844085077716406669252,
            depositAmount: 2819808950000000000000
        });
        entries[570] = MintEntry({
            tokenId: 748,
            user: 0xA582FdDE3D790b3AdF36F121abC97bbf727a942b,
            mintAmount: 92981611350434943853,
            depositAmount: 244664350000000000000
        });
        entries[571] = MintEntry({
            tokenId: 749,
            user: 0xA58A6eab55cf81D5e121758c1288D66FE4B74877,
            mintAmount: 39002384649018072243,
            depositAmount: 97810443360766840000
        });
        entries[572] = MintEntry({
            tokenId: 750,
            user: 0xA5B0bD4A037c2A1103f64A4b7420bE1271e977C9,
            mintAmount: 29179704062111848111,
            depositAmount: 69832048632421250000
        });
        entries[573] = MintEntry({
            tokenId: 751,
            user: 0xa5B51B9Cd891B3e1C97C02d9c74ea4F7bAdcDCEf,
            mintAmount: 60411719807644289157,
            depositAmount: 150000000000000000000
        });
        entries[574] = MintEntry({
            tokenId: 755,
            user: 0xA620546F0E6BC4A75DaF1328Af52D78908936223,
            mintAmount: 134708137031419829529,
            depositAmount: 334475175000000000000
        });
        entries[575] = MintEntry({
            tokenId: 756,
            user: 0xA6572B731865fF24705587dcdF5C3257249f0cA6,
            mintAmount: 466359122172135354183,
            depositAmount: 1178896933328544500000
        });
        entries[576] = MintEntry({
            tokenId: 757,
            user: 0xA6679503f27039d00066fF868288297aff784c9C,
            mintAmount: 4715397952387073829,
            depositAmount: 11210459364117164000
        });
        entries[577] = MintEntry({
            tokenId: 758,
            user: 0xA6a65874C8d725F4C8159c8A25D45a4E96640c31,
            mintAmount: 192408658653708502661,
            depositAmount: 400385700173485200000
        });
        entries[578] = MintEntry({
            tokenId: 759,
            user: 0xA7cc5536E3eAefB994AD85c09D426A120a5B7FB2,
            mintAmount: 181069389733741620017,
            depositAmount: 492934969154235400000
        });
        entries[579] = MintEntry({
            tokenId: 760,
            user: 0xA8047DcE2A42968379E68870274ED2F534082Edd,
            mintAmount: 42085135674686739351,
            depositAmount: 101869404424736330000
        });
        entries[580] = MintEntry({
            tokenId: 762,
            user: 0xA83EaC81093fD03170260C733cAAf1722be5342c,
            mintAmount: 41745689192172613106,
            depositAmount: 100000000000000000000
        });
        entries[581] = MintEntry({
            tokenId: 763,
            user: 0xa84A3B97Ba880C99cf90339eC17dea71EE3f0197,
            mintAmount: 285289706189348812100,
            depositAmount: 665220994543730000000
        });
        entries[582] = MintEntry({
            tokenId: 764,
            user: 0xA909be1aC709Bc08Bd8Cd69604CEe197360b3e33,
            mintAmount: 708355680423529450,
            depositAmount: 1989837664581593600
        });
        entries[583] = MintEntry({
            tokenId: 765,
            user: 0xa91428f80B317A7C7a71Bd3bc3917504C08203B6,
            mintAmount: 112858886638213999562,
            depositAmount: 268476930378116200000
        });
        entries[584] = MintEntry({
            tokenId: 766,
            user: 0xa927344A3144b68B272Ca944D3cDec0555a3FbdF,
            mintAmount: 61369896808214454843,
            depositAmount: 131325262470166600000
        });
        entries[585] = MintEntry({
            tokenId: 768,
            user: 0xA9b181a56ac5919902dF00981953A67F5e59E3cE,
            mintAmount: 398256432575003219898,
            depositAmount: 950000000000000000000
        });
        entries[586] = MintEntry({
            tokenId: 770,
            user: 0xaA6f09C75d1Ca7E05eB81e5cb0FdFF28d24CD416,
            mintAmount: 85730814109291603915,
            depositAmount: 199733618889077900000
        });
        entries[587] = MintEntry({
            tokenId: 772,
            user: 0xAAb9175b6eB327CdCC5589f9AEBcF23832Ff9329,
            mintAmount: 181606186753800134055,
            depositAmount: 410000000000000000000
        });
        entries[588] = MintEntry({
            tokenId: 774,
            user: 0xAb4eE2E1F45A8d43CACd3fdD3CcB45Ad96791ae8,
            mintAmount: 416071348312890992061,
            depositAmount: 1000000000000000000000
        });
        entries[589] = MintEntry({
            tokenId: 775,
            user: 0xaB8B5f7D4afb78B7aC8de4Ad4a8E131c58653b34,
            mintAmount: 77638718482196712037,
            depositAmount: 185449048720288900000
        });
        entries[590] = MintEntry({
            tokenId: 776,
            user: 0xAc189c0e3C5B91A2d3D285139353d778EFD15eeA,
            mintAmount: 75977305737534825062,
            depositAmount: 192798958200000000000
        });
        entries[591] = MintEntry({
            tokenId: 777,
            user: 0xaC237C34Bf06d7D723dE247931D9AEa5b2cde33f,
            mintAmount: 234675369170893289433,
            depositAmount: 616111253160600800000
        });
        entries[592] = MintEntry({
            tokenId: 778,
            user: 0xAC75706dFd5d8Aa9c8D465F08617c850dc368857,
            mintAmount: 39356384879378486897,
            depositAmount: 94158300000000000000
        });
        entries[593] = MintEntry({
            tokenId: 779,
            user: 0xAC87234B21240CdA556bc4EE81eFd9E370fA1696,
            mintAmount: 3653755680529906328433,
            depositAmount: 7529837167495600000000
        });
        entries[594] = MintEntry({
            tokenId: 780,
            user: 0xaCfE4511CE883C14c4eA40563F176C3C09b4c47C,
            mintAmount: 203117159871894060524,
            depositAmount: 500000000000000000000
        });
        entries[595] = MintEntry({
            tokenId: 781,
            user: 0xAd69dBC2cC49F3fF3122D63F2031ddc75Cc2A2EB,
            mintAmount: 3793776801564012855846,
            depositAmount: 7703813529688984000000
        });
        entries[596] = MintEntry({
            tokenId: 782,
            user: 0xad6EE7C40d7D80a6c404E82e77Cde5c5088E98a5,
            mintAmount: 322889446406950465056,
            depositAmount: 1000000000000000000000
        });
        entries[597] = MintEntry({
            tokenId: 783,
            user: 0xAd75835a3581046E639bD19e98011736df4DE861,
            mintAmount: 353254964638380191496,
            depositAmount: 950000000000000000000
        });
        entries[598] = MintEntry({
            tokenId: 784,
            user: 0xaD7B192c486009B5c66676d3Be3919321cFfC84D,
            mintAmount: 18746382723999383668,
            depositAmount: 45000000000000000000
        });
        entries[599] = MintEntry({
            tokenId: 785,
            user: 0xadA036edBc647D0212d9d841Ff91ba8F0F27CA89,
            mintAmount: 2208315880059924883531,
            depositAmount: 5272503679999999000000
        });
        entries[600] = MintEntry({
            tokenId: 786,
            user: 0xAdc8f4bD423e12CE815762F3d76ec574A22fda0D,
            mintAmount: 187532814097823961158,
            depositAmount: 493905010000000000000
        });
        entries[601] = MintEntry({
            tokenId: 787,
            user: 0xAE356Be6604c312179655d3890B3a3E4CAd119f8,
            mintAmount: 81604901177258452781,
            depositAmount: 195566518879855700000
        });
        entries[602] = MintEntry({
            tokenId: 788,
            user: 0xAE3D594a5d05e6dF446358eB4217BdC8Cce5870D,
            mintAmount: 215639321336834326761,
            depositAmount: 494000000000000000000
        });
        entries[603] = MintEntry({
            tokenId: 789,
            user: 0xae543c8A86CC7d0437687E7778fdb771efE0b322,
            mintAmount: 7621116986387292035,
            depositAmount: 20632954942264210000
        });
        entries[604] = MintEntry({
            tokenId: 790,
            user: 0xaF07C492Bd1CCfBF1fb644fC8Ab5B54aC4D93244,
            mintAmount: 4174067821532878133900,
            depositAmount: 10227298027919483000000
        });
        entries[605] = MintEntry({
            tokenId: 791,
            user: 0xAF10FE2402ECCc8181b5c6d093fa46079b831BB7,
            mintAmount: 18356829854631530452,
            depositAmount: 44698408000000000000
        });
        entries[606] = MintEntry({
            tokenId: 792,
            user: 0xAf36197FDC5d30F7aCCde6a0246A9CBdF663B0F0,
            mintAmount: 41607134831288199206,
            depositAmount: 100000000000000000000
        });
        entries[607] = MintEntry({
            tokenId: 793,
            user: 0xAf3DD6A7b3119e48E8028b12D9218ef5D4163B8B,
            mintAmount: 2042715341241469436547,
            depositAmount: 5147514860557137000000
        });
        entries[608] = MintEntry({
            tokenId: 794,
            user: 0xAFa6F7A00e089059DB60268ad230aF5e311C440c,
            mintAmount: 1311810075462902151845,
            depositAmount: 3216132733630000000000
        });
        entries[609] = MintEntry({
            tokenId: 795,
            user: 0xAFFFAD153363c29F068c0a2814C04F9eaA381fF1,
            mintAmount: 7592750770258489237209,
            depositAmount: 23278176261861167000000
        });
        entries[610] = MintEntry({
            tokenId: 796,
            user: 0xb00e6CcAf17861AeEBF340418D9B644BB05d60CD,
            mintAmount: 258611297370553950408,
            depositAmount: 608360353800000000000
        });
        entries[611] = MintEntry({
            tokenId: 798,
            user: 0xB0B60678A3571c46fD3861a83ea0Db2549986f9c,
            mintAmount: 688495234921761661483,
            depositAmount: 1598963212570000000000
        });
        entries[612] = MintEntry({
            tokenId: 799,
            user: 0xB0E1b094b3d7A02ac16f38bBF38a8beCd72eCd3d,
            mintAmount: 83940548586942349209,
            depositAmount: 200000000000000000000
        });
        entries[613] = MintEntry({
            tokenId: 801,
            user: 0xB11b61d2CF006fa241d2A57ad294a49f188fc7a5,
            mintAmount: 319350161494865138707,
            depositAmount: 793293755361516000000
        });
        entries[614] = MintEntry({
            tokenId: 802,
            user: 0xB1E1Be1B4F00a5E322824CAFAC8CA077922FEEA3,
            mintAmount: 3162566534545032269085,
            depositAmount: 10143672804980000000000
        });
        entries[615] = MintEntry({
            tokenId: 803,
            user: 0xB201e7399F718Fd52c5f04CE38fF780093734320,
            mintAmount: 50075628112274928174,
            depositAmount: 157997073000000000000
        });
        entries[616] = MintEntry({
            tokenId: 805,
            user: 0xB26391653be4fC965C31F29ec5d8163f26d1b91f,
            mintAmount: 1005200461675184039952,
            depositAmount: 3025923713424876000000
        });
        entries[617] = MintEntry({
            tokenId: 806,
            user: 0xB2A2a6a69E7A0aD66943F4c2869d45A9919CF740,
            mintAmount: 42507339952967243535,
            depositAmount: 99848267419265900000
        });
        entries[618] = MintEntry({
            tokenId: 807,
            user: 0xb2E2F0091E7cA37C754889301e6539677762b8d3,
            mintAmount: 353559761921797925418,
            depositAmount: 913932590000000000000
        });
        entries[619] = MintEntry({
            tokenId: 808,
            user: 0xb32E86A789432Bb61517C774E57F3FC0d2aA872B,
            mintAmount: 249290284233354418725,
            depositAmount: 499999099689090000000
        });
        entries[620] = MintEntry({
            tokenId: 809,
            user: 0xb32f980384092d7d63F6624c887669c76c386F5c,
            mintAmount: 2536117983871980623982,
            depositAmount: 5672655902850000000000
        });
        entries[621] = MintEntry({
            tokenId: 810,
            user: 0xb35DB7224dF14Ef461F95c70aA7f253E6b7fD6E7,
            mintAmount: 42012988046494974427,
            depositAmount: 102000000000000000000
        });
        entries[622] = MintEntry({
            tokenId: 811,
            user: 0xB383a8CF33E457045eed30f71aDFDBA4784D55D6,
            mintAmount: 976316888022619216949,
            depositAmount: 2252017677265733700000
        });
        entries[623] = MintEntry({
            tokenId: 812,
            user: 0xB3D0204E133b24B455d49d9F87b6D1c605435ACC,
            mintAmount: 73460121659524180812,
            depositAmount: 200000000000000000000
        });
        entries[624] = MintEntry({
            tokenId: 814,
            user: 0xb4101e9B1e7F079309d44De1F34D79d74aB47975,
            mintAmount: 61952974453677444074,
            depositAmount: 168134893279999980000
        });
        entries[625] = MintEntry({
            tokenId: 815,
            user: 0xb432cA713b50c72049493EdfDE314AbeFD23BeD9,
            mintAmount: 105836922176442050355,
            depositAmount: 229483527528722400000
        });
        entries[626] = MintEntry({
            tokenId: 816,
            user: 0xB43500e9Ec92C8A14fc2223754330B08E0F2b65d,
            mintAmount: 39319040406066478641,
            depositAmount: 92359062352002150000
        });
        entries[627] = MintEntry({
            tokenId: 817,
            user: 0xb44Cc8cD4105A2673eF3A584182e8764B83B1c13,
            mintAmount: 5158385071210294763,
            depositAmount: 12316030000000000000
        });
        entries[628] = MintEntry({
            tokenId: 818,
            user: 0xB4C3312D8e9f680FFb1eF4Ba2Ca05387532a4d47,
            mintAmount: 792118608728000428596,
            depositAmount: 2500000000000000000000
        });
        entries[629] = MintEntry({
            tokenId: 819,
            user: 0xB4Ea25B9b43887771cE3598486c7E598EF841494,
            mintAmount: 12703175092701723772,
            depositAmount: 30000000000000000000
        });
        entries[630] = MintEntry({
            tokenId: 820,
            user: 0xb4ec0953bAc7a88b9E44e50f95A3c67bDD287eC5,
            mintAmount: 231688449136331666091,
            depositAmount: 504493325410882550000
        });
        entries[631] = MintEntry({
            tokenId: 822,
            user: 0xB5a34FD654b6bfBd2e48e8F9D6f76ce0fFa92a58,
            mintAmount: 62584603601737933988,
            depositAmount: 148485195640000000000
        });
        entries[632] = MintEntry({
            tokenId: 823,
            user: 0xb5C0e552CF17a544FA0eE235539844a4A40500D4,
            mintAmount: 408176790229755396116,
            depositAmount: 984500000000000000000
        });
        entries[633] = MintEntry({
            tokenId: 824,
            user: 0xB5C327EF90eC4Ed329321D0f5F30294289B94560,
            mintAmount: 25569534170994830509646,
            depositAmount: 52021705159725660000000
        });
        entries[634] = MintEntry({
            tokenId: 825,
            user: 0xB5Fe01d2BAf99362057eC0d17689BcFAf4631Ca3,
            mintAmount: 5619690463787342547,
            depositAmount: 11899898391058133000
        });
        entries[635] = MintEntry({
            tokenId: 826,
            user: 0xb6AE9F6804B9d2E472Ab682e6220493f5CfABB59,
            mintAmount: 8155776570679675387,
            depositAmount: 19350000000000000000
        });
        entries[636] = MintEntry({
            tokenId: 827,
            user: 0xb6Bc98F5D7F6CE3c0946f7675128ab673e6c5D41,
            mintAmount: 312516696352849788965,
            depositAmount: 850472877433896300000
        });
        entries[637] = MintEntry({
            tokenId: 828,
            user: 0xB73f7F645eB32fc641508F474089c5226C97Bb11,
            mintAmount: 108789077196828747571,
            depositAmount: 232797427725971800000
        });
        entries[638] = MintEntry({
            tokenId: 829,
            user: 0xB7666197F53636C22349cc48a5a6b521E4015e33,
            mintAmount: 629393623980974342366,
            depositAmount: 1448812513413535000000
        });
        entries[639] = MintEntry({
            tokenId: 830,
            user: 0xB83a5c21bC188a53135E41EfE9deF3E0a01f4755,
            mintAmount: 207148675042667683520,
            depositAmount: 500000000000000000000
        });
        entries[640] = MintEntry({
            tokenId: 831,
            user: 0xb8c5b85B3F1Cf335a0cA31D099832db4157ab5e3,
            mintAmount: 165548987334714176017,
            depositAmount: 400000000000000000000
        });
        entries[641] = MintEntry({
            tokenId: 832,
            user: 0xb912f4EAd8B8b04B59662bE1053A9c9e998161Ad,
            mintAmount: 49705542111882160074,
            depositAmount: 134999939336790000000
        });
        entries[642] = MintEntry({
            tokenId: 833,
            user: 0xb9359b722515aD029BC89BF2019E7dd189fD1Bcd,
            mintAmount: 234830347563229657443,
            depositAmount: 569783080310026700000
        });
        entries[643] = MintEntry({
            tokenId: 834,
            user: 0xB9857C59406105F49b6682dA8a55CA2d93c32c00,
            mintAmount: 194552193298351805189,
            depositAmount: 478549483218101300000
        });
        entries[644] = MintEntry({
            tokenId: 835,
            user: 0xB9E00Eac34d3c105e88BF0CcCFF614eCBf55Ced7,
            mintAmount: 3427277686002897320285,
            depositAmount: 7637863181870000000000
        });
        entries[645] = MintEntry({
            tokenId: 836,
            user: 0xBA19BA5233b49794c33f01654e99A60E579E6f29,
            mintAmount: 397871176653585947432,
            depositAmount: 981040857660000000000
        });
        entries[646] = MintEntry({
            tokenId: 837,
            user: 0xba4C73ef5C455E2D5eE63eAEe3C4baA9b2030270,
            mintAmount: 172270886338278161572,
            depositAmount: 412084918850294050000
        });
        entries[647] = MintEntry({
            tokenId: 838,
            user: 0xbA58Aad81BA65DE665f197798CAEf54CeE813F10,
            mintAmount: 65066577400190963764,
            depositAmount: 175745679106028100000
        });
        entries[648] = MintEntry({
            tokenId: 840,
            user: 0xBac33bE0317b0ae47B38701315c460A821871d23,
            mintAmount: 63601450064778432948,
            depositAmount: 144739430700000000000
        });
        entries[649] = MintEntry({
            tokenId: 841,
            user: 0xBAfa7D6Ef8F834A59914c1dBc6Dd068dB5668337,
            mintAmount: 989677715078606783217,
            depositAmount: 2222674347563485000000
        });
        entries[650] = MintEntry({
            tokenId: 844,
            user: 0xBB6b65f658C834cacBf6B029C4dc983735D59226,
            mintAmount: 42662750659028667071,
            depositAmount: 110005484150000000000
        });
        entries[651] = MintEntry({
            tokenId: 845,
            user: 0xBBD2bCb175396d9ac5C18A6797943F1B62b30b23,
            mintAmount: 82759918767458798595,
            depositAmount: 198247820000000000000
        });
        entries[652] = MintEntry({
            tokenId: 847,
            user: 0xBC6e0e589845f9a59Fa0DC47Cf4741e0233A9c41,
            mintAmount: 391260726122351050921,
            depositAmount: 1036686628369890400000
        });
        entries[653] = MintEntry({
            tokenId: 848,
            user: 0xBc825866a4d39c7177c513Dc2e59A67d72d1E9FA,
            mintAmount: 855235589190815768095,
            depositAmount: 2011098137285025000000
        });
        entries[654] = MintEntry({
            tokenId: 850,
            user: 0xBcaf219BA7C5299892b074D69398564dfdfE79f3,
            mintAmount: 37171984900941159883,
            depositAmount: 101253475594210030000
        });
        entries[655] = MintEntry({
            tokenId: 851,
            user: 0xbcC4a5D73032fcaF8b7a4d5C843f7A25a9B92914,
            mintAmount: 7037455427013528820,
            depositAmount: 16762540934111396000
        });
        entries[656] = MintEntry({
            tokenId: 852,
            user: 0xBCccA1E452445532EbC495Fe14B0A1Cd36d46EbC,
            mintAmount: 39679793770987860844,
            depositAmount: 159918240000000000000
        });
        entries[657] = MintEntry({
            tokenId: 853,
            user: 0xbD0922d4D895FaE0322FD5aC137126bf56Fbcf71,
            mintAmount: 3139911254670851416361,
            depositAmount: 9067689534518510000000
        });
        entries[658] = MintEntry({
            tokenId: 854,
            user: 0xBd8C01FFC09ca2Dac732B8c942d7f0dd2aa78Eb1,
            mintAmount: 109119076387794127665,
            depositAmount: 249999701498035000000
        });
        entries[659] = MintEntry({
            tokenId: 856,
            user: 0xBDfb0e31E108cb6c394216c6bC83Ce4829D84427,
            mintAmount: 41948991895258640706,
            depositAmount: 100000000000000000000
        });
        entries[660] = MintEntry({
            tokenId: 857,
            user: 0xbe535c49d8e65DA9cd9a809A3D59248A89A2496B,
            mintAmount: 6679661851376926174127,
            depositAmount: 25000060197020826000000
        });
        entries[661] = MintEntry({
            tokenId: 858,
            user: 0xBEa1eFeEd7537236c577b321Ca49fb394b6dc7Dd,
            mintAmount: 5929372806354267056,
            depositAmount: 31624622245705003000
        });
        entries[662] = MintEntry({
            tokenId: 860,
            user: 0xBF8fE120F4Bb49de7DaaaC892fb7A532673A9B12,
            mintAmount: 93449968048600788379,
            depositAmount: 245000000000000000000
        });
        entries[663] = MintEntry({
            tokenId: 861,
            user: 0xbFB2CAD464868B5705e2F625BB52C909204A39E3,
            mintAmount: 790666537118167999251,
            depositAmount: 1998705099950976000000
        });
        entries[664] = MintEntry({
            tokenId: 862,
            user: 0xBfc3f319C16AC24746a3a41c397b80fCB0c7E4D2,
            mintAmount: 2089125430721765738091,
            depositAmount: 4987928412290000000000
        });
        entries[665] = MintEntry({
            tokenId: 863,
            user: 0xc02FAdedC679cEc2889BbAF8997caA1A7e06231E,
            mintAmount: 1369918349146472561784,
            depositAmount: 4346919655697905000000
        });
        entries[666] = MintEntry({
            tokenId: 864,
            user: 0xc07c461d1c91A9eCD6f2A2f57eC3e7CaaCf2bba2,
            mintAmount: 522904702360590341649,
            depositAmount: 1330768145286270000000
        });
        entries[667] = MintEntry({
            tokenId: 865,
            user: 0xC0F2a8CC7B785A774FB00EeA2b529CC39fBc2e50,
            mintAmount: 2956407205281466063084,
            depositAmount: 6326851582591983000000
        });
        entries[668] = MintEntry({
            tokenId: 867,
            user: 0xc0F6bd9F0BE7E08b51f65B82fC95A19Df826F0fE,
            mintAmount: 179417526232530699028,
            depositAmount: 500000000000000000000
        });
        entries[669] = MintEntry({
            tokenId: 868,
            user: 0xc139fc26C6b73b878d8588F98D2D4B89C94844E1,
            mintAmount: 545631073233439272636,
            depositAmount: 1129765811210000000000
        });
        entries[670] = MintEntry({
            tokenId: 869,
            user: 0xC16623Cb1505c57C56B3dd9633DbB43991ab2804,
            mintAmount: 144439520565179971102,
            depositAmount: 500000323290000000000
        });
        entries[671] = MintEntry({
            tokenId: 871,
            user: 0xc19Fb917e9b674A1645599ba1E225d03956c3AC5,
            mintAmount: 435981456655503722992,
            depositAmount: 1176610145127633000000
        });
        entries[672] = MintEntry({
            tokenId: 873,
            user: 0xC208C84FC1B7A11ac3C798B396f9c0e5a23CFA38,
            mintAmount: 556024253541970434168,
            depositAmount: 1478470536973241800000
        });
        entries[673] = MintEntry({
            tokenId: 874,
            user: 0xc2328A29637c3b3e3352c8A450355B82421eE19C,
            mintAmount: 2410487795771175588172,
            depositAmount: 7121755957389969000000
        });
        entries[674] = MintEntry({
            tokenId: 875,
            user: 0xC233dC78f806618d79251Aec3A0e5aEE249a37D0,
            mintAmount: 626229637131659489131,
            depositAmount: 1501100000000000000000
        });
        entries[675] = MintEntry({
            tokenId: 876,
            user: 0xc2EeAdC3737510C32B1b1049c6B8e857482b300E,
            mintAmount: 470418979790081101217,
            depositAmount: 1072982826229029100000
        });
        entries[676] = MintEntry({
            tokenId: 877,
            user: 0xc2FD7a511E09FDA0b6C2fe043EFed91c512fC1D5,
            mintAmount: 20859024619666593403,
            depositAmount: 50000000000000000000
        });
        entries[677] = MintEntry({
            tokenId: 878,
            user: 0xC3268DDB8E38302763fFdC9191FCEbD4C948fe1b,
            mintAmount: 719630359905918376524,
            depositAmount: 1666622312979647400000
        });
        entries[678] = MintEntry({
            tokenId: 880,
            user: 0xC3Ab8A45e70C49a94a36122f3159ba95D3f2daE0,
            mintAmount: 42787971733163833519,
            depositAmount: 102000000000000000000
        });
        entries[679] = MintEntry({
            tokenId: 881,
            user: 0xC3bd40359a5B5f85507Abf4Bba212B97D9b017Ef,
            mintAmount: 41233930593191149621,
            depositAmount: 99893061013665600000
        });
        entries[680] = MintEntry({
            tokenId: 882,
            user: 0xC3e62dAEb84894097e13086Fcd6011F4FBabCde7,
            mintAmount: 47509123568335348522,
            depositAmount: 100000000000000000000
        });
        entries[681] = MintEntry({
            tokenId: 884,
            user: 0xC42008F4AaDc0b487F214d738fCdCea1D0488e9D,
            mintAmount: 272873093777569579870,
            depositAmount: 644099341350239700000
        });
        entries[682] = MintEntry({
            tokenId: 885,
            user: 0xc4320AC0c819f135757D168da2c303F258c6135e,
            mintAmount: 53201760608818762521,
            depositAmount: 133042957550000000000
        });
        entries[683] = MintEntry({
            tokenId: 886,
            user: 0xc4358dc65c840813f2e89e8AE06686a581BAA7FA,
            mintAmount: 186756577916342081812,
            depositAmount: 485419460840000000000
        });
        entries[684] = MintEntry({
            tokenId: 887,
            user: 0xC4577824061AC8a3B249e14bFa5f0183D6dBBEc0,
            mintAmount: 7080218561684876849406,
            depositAmount: 21500000000000000000000
        });
        entries[685] = MintEntry({
            tokenId: 889,
            user: 0xC4c03919345b3157e749cc5deA18B0470284C08F,
            mintAmount: 242628773293714466486,
            depositAmount: 530000000000000000000
        });
        entries[686] = MintEntry({
            tokenId: 890,
            user: 0xC4d9d1a93068d311Ab18E988244123430eB4F1CD,
            mintAmount: 16695725212185724766,
            depositAmount: 43255583121836106000
        });
        entries[687] = MintEntry({
            tokenId: 892,
            user: 0xc5259CC500564de27ca78BBC0FAC4727DF72c43d,
            mintAmount: 8345487933972095128,
            depositAmount: 20000000000683397000
        });
        entries[688] = MintEntry({
            tokenId: 893,
            user: 0xC5bCa8D9E692612Fd411736cBf9e19f68F22dbc1,
            mintAmount: 20123964873358339439,
            depositAmount: 45914939673466300000
        });
        entries[689] = MintEntry({
            tokenId: 894,
            user: 0xC6411350766ED10630579da82D232bCE7f33869C,
            mintAmount: 4324233931739030943665,
            depositAmount: 8999402099000001000000
        });
        entries[690] = MintEntry({
            tokenId: 895,
            user: 0xC6987A93a3Ff8441351041caA5bAD8c16aCF7bc9,
            mintAmount: 120633562386167895339,
            depositAmount: 299528542070000000000
        });
        entries[691] = MintEntry({
            tokenId: 896,
            user: 0xC6F01A13BB3089089168eC992d0aC49bfb122594,
            mintAmount: 39903855670857185438,
            depositAmount: 114416975947402300000
        });
        entries[692] = MintEntry({
            tokenId: 902,
            user: 0xc83cCcd964FAe2174749A3B5CAe65d6C60c28Db2,
            mintAmount: 3666533650504683890,
            depositAmount: 9999998416970000000
        });
        entries[693] = MintEntry({
            tokenId: 903,
            user: 0xC926ADDF7133DF6238164568485A184320D636A1,
            mintAmount: 112903472171815188720,
            depositAmount: 284378907040000000000
        });
        entries[694] = MintEntry({
            tokenId: 904,
            user: 0xC93832E75d4B71a1D25a39DaF12157237fEEd735,
            mintAmount: 746139418969700266,
            depositAmount: 2009471385970053000
        });
        entries[695] = MintEntry({
            tokenId: 905,
            user: 0xc9850118D42feB44885678b31EB6fB3971374609,
            mintAmount: 398078645356629209054,
            depositAmount: 1000000000000000000000
        });
        entries[696] = MintEntry({
            tokenId: 906,
            user: 0xca8419a56b7E8A3a38f5653A2f72656376DF17e7,
            mintAmount: 23261022000000000000,
            depositAmount: 46521999052920000000
        });
        entries[697] = MintEntry({
            tokenId: 907,
            user: 0xCb01F3D84F125667F87Ed21a6C3854021C9d90DB,
            mintAmount: 219874746885227351869,
            depositAmount: 529352999040910700000
        });
        entries[698] = MintEntry({
            tokenId: 908,
            user: 0xCB354ACbb1180EC2eD0B98e2b57Ae78870a074B7,
            mintAmount: 468576860775694770738,
            depositAmount: 1183956907490000000000
        });
        entries[699] = MintEntry({
            tokenId: 909,
            user: 0xcb44375bA55a072A8A43452F9F6F1e24AEbf4666,
            mintAmount: 328193067395324380329,
            depositAmount: 986129720490000000000
        });
        entries[700] = MintEntry({
            tokenId: 910,
            user: 0xCb636A55b1B9C64f5d9fD84662400cB08f8c1df8,
            mintAmount: 90502489416808968638,
            depositAmount: 200523714763717640000
        });
        entries[701] = MintEntry({
            tokenId: 911,
            user: 0xcBc2dA0dB2940dB0F211d67D7F14ad1057794F68,
            mintAmount: 75319300613091995840,
            depositAmount: 173000000000000000000
        });
        entries[702] = MintEntry({
            tokenId: 912,
            user: 0xcBc853eFCf3f0A78C6F52828Ad6a8091a8B302B3,
            mintAmount: 8607857737093636061882,
            depositAmount: 17217634932609109000000
        });
        entries[703] = MintEntry({
            tokenId: 913,
            user: 0xcbFdCD7409F760081f33DE2C87288DD30153c353,
            mintAmount: 1233510263035578270589,
            depositAmount: 2888802289685108000000
        });
        entries[704] = MintEntry({
            tokenId: 914,
            user: 0xCc27Fd7C81D49CfBf29d31a174E2d82CA0242301,
            mintAmount: 3178460643554576099972,
            depositAmount: 9213830814009776000000
        });
        entries[705] = MintEntry({
            tokenId: 915,
            user: 0xcc804BD0a2537C227428e64226CD9E6863f31707,
            mintAmount: 53639602094488266896,
            depositAmount: 127038516310000000000
        });
        entries[706] = MintEntry({
            tokenId: 916,
            user: 0xCc93b05125C167047D11F0208E05B1D5848a88d1,
            mintAmount: 40236278084715046787,
            depositAmount: 93652172072637640000
        });
        entries[707] = MintEntry({
            tokenId: 917,
            user: 0xccb98208a3c87EC4B86A65c4b69Bcf7378ca434A,
            mintAmount: 18564140480839735523,
            depositAmount: 49999979994910000000
        });
        entries[708] = MintEntry({
            tokenId: 918,
            user: 0xCcc4CE35F08A0EcC3afE07781104aa088A795a18,
            mintAmount: 340328923950324653123,
            depositAmount: 815243275500000000000
        });
        entries[709] = MintEntry({
            tokenId: 919,
            user: 0xCcd84b249c0F8dC19abc098E6f9c0E5F5A900617,
            mintAmount: 234494917107986688093,
            depositAmount: 554025326060699000000
        });
        entries[710] = MintEntry({
            tokenId: 921,
            user: 0xCd629023071e10B354c949d03Da150Bf1907faFD,
            mintAmount: 416229178108502296586,
            depositAmount: 991723750000000000000
        });
        entries[711] = MintEntry({
            tokenId: 922,
            user: 0xcDd535328a10B84Ff64d69858C795A5C26981791,
            mintAmount: 4271056858521156414211,
            depositAmount: 8934418864529606000000
        });
        entries[712] = MintEntry({
            tokenId: 923,
            user: 0xCe251d7f192486804943A030c3Fa7ce3820A1466,
            mintAmount: 11019018248927777122,
            depositAmount: 30000000000000000000
        });
        entries[713] = MintEntry({
            tokenId: 924,
            user: 0xcE7c72e8127E994bcEa5F000FAbF64E6ea50F5b8,
            mintAmount: 566473660834755671553,
            depositAmount: 1192347107855949000000
        });
        entries[714] = MintEntry({
            tokenId: 927,
            user: 0xcF6b6CB97aD9dD5B1877DFbC6D9B64157DCd8C8E,
            mintAmount: 2026840345910270545847,
            depositAmount: 5219194969824898000000
        });
        entries[715] = MintEntry({
            tokenId: 928,
            user: 0xCF8BAF60A43ECA451e12D11a6DaF3fFa3474FfFD,
            mintAmount: 103196283296058000163,
            depositAmount: 229978182366670500000
        });
        entries[716] = MintEntry({
            tokenId: 929,
            user: 0xcFc17B9B0Cae7428098A1Bc4a57f19DAcb5db657,
            mintAmount: 19474221841139806934,
            depositAmount: 49999907860532000000
        });
        entries[717] = MintEntry({
            tokenId: 930,
            user: 0xD0099fe0411B4CD1edf021f0aEeB12B9194b2742,
            mintAmount: 58806542117920847001,
            depositAmount: 147500000000000000000
        });
        entries[718] = MintEntry({
            tokenId: 932,
            user: 0xD015BC3fedF5E9455d8688Fee238e15B6fBDF544,
            mintAmount: 104216345841950489379,
            depositAmount: 247000000000000000000
        });
        entries[719] = MintEntry({
            tokenId: 933,
            user: 0xd05d9c16b666075649e52c767d0069c9f4F04AaC,
            mintAmount: 77056526134897656512,
            depositAmount: 183677728447766630000
        });
        entries[720] = MintEntry({
            tokenId: 934,
            user: 0xD0a2Fe011342c2E59A81866aE5Bbd6E13C6C572f,
            mintAmount: 688726392987695616902,
            depositAmount: 1550844708660000000000
        });
        entries[721] = MintEntry({
            tokenId: 935,
            user: 0xd0f3B04F6066CfEAd18a24A8458A18F1D7F7007D,
            mintAmount: 218710979651648277773,
            depositAmount: 970957724114190600000
        });
        entries[722] = MintEntry({
            tokenId: 936,
            user: 0xD19B1905e5E7204240D32D1B841251f76cf1Eb49,
            mintAmount: 305107180948759546980,
            depositAmount: 726735915130986600000
        });
        entries[723] = MintEntry({
            tokenId: 938,
            user: 0xd1c7314F7c470CB27232A4Ff77E451C640cdf0cA,
            mintAmount: 133393483682239643473,
            depositAmount: 316288652541728850000
        });
        entries[724] = MintEntry({
            tokenId: 939,
            user: 0xD2d24db10c43811302780e082A3E6f73a97eA48F,
            mintAmount: 22171424843612968146484,
            depositAmount: 47026725601568510000000
        });
        entries[725] = MintEntry({
            tokenId: 941,
            user: 0xD3055aE6117Fd4c72444aD3443c42F820269b90C,
            mintAmount: 1203527984469467428728,
            depositAmount: 2863761910994742000000
        });
        entries[726] = MintEntry({
            tokenId: 944,
            user: 0xD34eCcaF180a75b56CE98d0c414D3FC03A820f58,
            mintAmount: 183276170915707137089,
            depositAmount: 499999906743570000000
        });
        entries[727] = MintEntry({
            tokenId: 946,
            user: 0xD3c4892807453F93a34965F511a313157C16Fa80,
            mintAmount: 376392918405764837757,
            depositAmount: 999999999999998800000
        });
        entries[728] = MintEntry({
            tokenId: 947,
            user: 0xd419d53817E1DAA7B2f72E51707774f3ff0A54A3,
            mintAmount: 1457458908849336124875,
            depositAmount: 3970000000000000000000
        });
        entries[729] = MintEntry({
            tokenId: 948,
            user: 0xd42ccAa658d460b5DfBCEe6bbbeAF1B6667a30F1,
            mintAmount: 140752045484696949658,
            depositAmount: 291436570692616520000
        });
        entries[730] = MintEntry({
            tokenId: 949,
            user: 0xd4789917D827809F32108d060eAd11e907702630,
            mintAmount: 2774160732492025126104,
            depositAmount: 9988110150000000000000
        });
        entries[731] = MintEntry({
            tokenId: 952,
            user: 0xD4CA789F73d87aAF87d31b558ec7F1E159849Ed6,
            mintAmount: 184445552955177990235,
            depositAmount: 411046325113798660000
        });
        entries[732] = MintEntry({
            tokenId: 953,
            user: 0xd4d278Ba628a03564D7980E08038F10af7070F36,
            mintAmount: 1939703542312120581,
            depositAmount: 4999995178505000000
        });
        entries[733] = MintEntry({
            tokenId: 954,
            user: 0xD51403740F75bfA64704b4d1f5C2a099eFC560d0,
            mintAmount: 195853142591719385930,
            depositAmount: 475000000000000000000
        });
        entries[734] = MintEntry({
            tokenId: 955,
            user: 0xd521E9f3E94d7c75e2b82d11fDAAd0A4f5884eBD,
            mintAmount: 207551098865703940203,
            depositAmount: 660524397928735400000
        });
        entries[735] = MintEntry({
            tokenId: 957,
            user: 0xd5b45b38a93291DB4A49E074B296751d92E94397,
            mintAmount: 841185624811584404860,
            depositAmount: 1997659461245988000000
        });
        entries[736] = MintEntry({
            tokenId: 958,
            user: 0xD5bE0439eCCb370C807F698f6Ab98bAA5fBD24e0,
            mintAmount: 75252641626848525809,
            depositAmount: 200000000000000000000
        });
        entries[737] = MintEntry({
            tokenId: 959,
            user: 0xd5d41aE50Cd1Ff52c06D6c52A40A74D41eA1Ad3F,
            mintAmount: 21045519987662120855,
            depositAmount: 46000000000000000000
        });
        entries[738] = MintEntry({
            tokenId: 961,
            user: 0xd6587009D4b1904E7849148d8e2317324B678c67,
            mintAmount: 25474980038618051374,
            depositAmount: 69287574299477250000
        });
        entries[739] = MintEntry({
            tokenId: 962,
            user: 0xD6D76C84bb2342A95c54058354A881CEBa9DFd75,
            mintAmount: 103488347355648351189,
            depositAmount: 247500000000000000000
        });
        entries[740] = MintEntry({
            tokenId: 963,
            user: 0xd7CDEa567a6aa9cBD81fd9aec7b39f94419cFB4f,
            mintAmount: 20780501836330670403,
            depositAmount: 50000000000000000000
        });
        entries[741] = MintEntry({
            tokenId: 964,
            user: 0xD7e25378bFF3ab51DCd716e7C013DEa98c4D51d5,
            mintAmount: 319402025124662852028,
            depositAmount: 999230740000000000000
        });
        entries[742] = MintEntry({
            tokenId: 965,
            user: 0xd7Ee758A2666AB81e8657f69E280531E562F99C0,
            mintAmount: 100061058874422397118,
            depositAmount: 239322175664459500000
        });
        entries[743] = MintEntry({
            tokenId: 966,
            user: 0xD7F5b60C598dA99045f3D4f6FE3F9120DA3C2976,
            mintAmount: 9348394932137578064,
            depositAmount: 25999967069765000000
        });
        entries[744] = MintEntry({
            tokenId: 967,
            user: 0xd82D2c69f91dfC1a21510D7811589da1969A82f0,
            mintAmount: 388970926601491135117,
            depositAmount: 965800000000000000000
        });
        entries[745] = MintEntry({
            tokenId: 968,
            user: 0xD86A07dd9739C54574a4Aec955Bac66D93c710e3,
            mintAmount: 30961852557086204483,
            depositAmount: 74349711173739510000
        });
        entries[746] = MintEntry({
            tokenId: 970,
            user: 0xd9832A299d700Da9aDCD0fE3c7Ba89d3D57DC252,
            mintAmount: 41982805061390843913,
            depositAmount: 99904391500000000000
        });
        entries[747] = MintEntry({
            tokenId: 972,
            user: 0xd9e7Cd452b450A07984124E53B10021866b2462F,
            mintAmount: 89158110235181209432,
            depositAmount: 203891392629214250000
        });
        entries[748] = MintEntry({
            tokenId: 973,
            user: 0xdA03Bca6E7E6017739d0535dd38e2553067D223a,
            mintAmount: 2605026607880516035,
            depositAmount: 6209537256377344000
        });
        entries[749] = MintEntry({
            tokenId: 974,
            user: 0xDa4Ab2BE19b4Eac7Bbc496a42DA8b06C7C7f15Cf,
            mintAmount: 186452628086526463954,
            depositAmount: 471827089049022700000
        });
        entries[750] = MintEntry({
            tokenId: 975,
            user: 0xDA5b2cd0d0Bb26E79FB3210233dDABdB7de131C9,
            mintAmount: 426289417945993396059,
            depositAmount: 1000000000000000000000
        });
        entries[751] = MintEntry({
            tokenId: 976,
            user: 0xDa5D28f67ee642968CF5528aa1cB2290E7B2E2D0,
            mintAmount: 1500781267720033198502,
            depositAmount: 3641436392129248000000
        });
        entries[752] = MintEntry({
            tokenId: 977,
            user: 0xdAcD619b131a15d0c8c99Add553D709F3f2a6A7c,
            mintAmount: 87253603431742668075,
            depositAmount: 208324501300000000000
        });
        entries[753] = MintEntry({
            tokenId: 979,
            user: 0xDb98D124b1e644c5D434ba5A3d865e5f18316477,
            mintAmount: 32163463104888974555,
            depositAmount: 77000000000000000000
        });
        entries[754] = MintEntry({
            tokenId: 980,
            user: 0xDC0b56461B17042B58886bd0Bd92007Ba416e999,
            mintAmount: 3857431565721903595,
            depositAmount: 11899302667774120000
        });
        entries[755] = MintEntry({
            tokenId: 981,
            user: 0xDC354F962BbBFb9e20761b38e55a6BB6F0CcAF4f,
            mintAmount: 30402994584354569205,
            depositAmount: 80000000000000000000
        });
        entries[756] = MintEntry({
            tokenId: 982,
            user: 0xdc4552ac1EF43539a6043a6FbB8904FDAe979020,
            mintAmount: 41826501550173316805,
            depositAmount: 100000000000000000000
        });
        entries[757] = MintEntry({
            tokenId: 983,
            user: 0xdc495516dDc20877E55E6e05162a990e9057fc66,
            mintAmount: 148761617077798558819,
            depositAmount: 400083000000000000000
        });
        entries[758] = MintEntry({
            tokenId: 985,
            user: 0xDC5Bb4F6126A5eD7D99AF7E56387db717c1042BD,
            mintAmount: 182689777754879224658,
            depositAmount: 435374558146746060000
        });
        entries[759] = MintEntry({
            tokenId: 986,
            user: 0xDc815efEF274725715aC1cF28980E1d76E24278F,
            mintAmount: 306540668356240959314,
            depositAmount: 813262585897360000000
        });
        entries[760] = MintEntry({
            tokenId: 987,
            user: 0xDcBE59C14C6A04fEA9e295D116B7a579582CE068,
            mintAmount: 1054994401447949902301,
            depositAmount: 3435447107459695000000
        });
        entries[761] = MintEntry({
            tokenId: 988,
            user: 0xDCe543698AB6242F0eAAA32a6a8325883302fcE5,
            mintAmount: 715624304011638341542,
            depositAmount: 1736868992650658000000
        });
        entries[762] = MintEntry({
            tokenId: 989,
            user: 0xDd9189f9Cb498f5dc729bAa19734475C22b36981,
            mintAmount: 1833598817008705556512,
            depositAmount: 5364959344882739000000
        });
        entries[763] = MintEntry({
            tokenId: 990,
            user: 0xDDf41B260DAc2757ab72393d635f46A533f8244E,
            mintAmount: 8029743646060611089,
            depositAmount: 47782709980214770000
        });
        entries[764] = MintEntry({
            tokenId: 991,
            user: 0xdE41501a3dA3e3b086Fd7ef6242af17013cD2cfD,
            mintAmount: 28615723232376538707669,
            depositAmount: 60494700609580000000000
        });
        entries[765] = MintEntry({
            tokenId: 993,
            user: 0xDe9E82B1Ac219F96744bd8aFD236113140A98A26,
            mintAmount: 663388912082894101630,
            depositAmount: 1715633280595812400000
        });
        entries[766] = MintEntry({
            tokenId: 995,
            user: 0xdf67361193D52EE42CB759eb98Ce2c7978DD440E,
            mintAmount: 367084894622775974922,
            depositAmount: 999412705370000000000
        });
        entries[767] = MintEntry({
            tokenId: 996,
            user: 0xDfFc750270c50777ae7fFa330Bb976535E0268a4,
            mintAmount: 495418592383765034642,
            depositAmount: 1195804395760000000000
        });
        entries[768] = MintEntry({
            tokenId: 997,
            user: 0xe08563966Aca5f5297CF58Ff11cF28ca660e0012,
            mintAmount: 909824380546507701097,
            depositAmount: 2180398288933720000000
        });
        entries[769] = MintEntry({
            tokenId: 998,
            user: 0xe0c5164D6eEd00D9A53FBA883C06E92428019813,
            mintAmount: 13822407671605980300,
            depositAmount: 28644721000000000000
        });
        entries[770] = MintEntry({
            tokenId: 999,
            user: 0xe0dFB09B94A80C66DA0e4FaA847CEa819cEcd33a,
            mintAmount: 464986964712873707,
            depositAmount: 5236663813965001000
        });
        entries[771] = MintEntry({
            tokenId: 1000,
            user: 0xe157eb51748964C423B433935F9d4C4205C02593,
            mintAmount: 410477676645010671970,
            depositAmount: 978020000000000000000
        });
        entries[772] = MintEntry({
            tokenId: 1001,
            user: 0xe19558D2b3fAbb5c045DdF3b44dC15dE18E9Cd20,
            mintAmount: 226986608070139661149,
            depositAmount: 538770695811823400000
        });
        entries[773] = MintEntry({
            tokenId: 1002,
            user: 0xE1A50c8da0C170b9784C33Ba74167dDe61CEE0d8,
            mintAmount: 32347172595659509635,
            depositAmount: 70015998660000000000
        });
        entries[774] = MintEntry({
            tokenId: 1003,
            user: 0xe2026e2d48Db82769BB4c912Cb8275cB48860Efd,
            mintAmount: 18590768610571451034258,
            depositAmount: 45733464629248000000000
        });
        entries[775] = MintEntry({
            tokenId: 1004,
            user: 0xe234b784fA421c0216cb22d4145fb0bB6fbD890b,
            mintAmount: 30444411477635373160,
            depositAmount: 64081189445318370000
        });
        entries[776] = MintEntry({
            tokenId: 1005,
            user: 0xe29576BC66051fEa9Ff50cBBFA8ff3284014bF9b,
            mintAmount: 624178896154700019141,
            depositAmount: 1420462015750000000000
        });
        entries[777] = MintEntry({
            tokenId: 1006,
            user: 0xe321bD63CDE8Ea046b382f82964575f2A5586474,
            mintAmount: 3650002397152183025,
            depositAmount: 19999981965340000000
        });
        entries[778] = MintEntry({
            tokenId: 1007,
            user: 0xE33dF35dC8B326c15c2a26A2bDBC81C797132507,
            mintAmount: 197987906717197422691,
            depositAmount: 500269000000000000000
        });
        entries[779] = MintEntry({
            tokenId: 1008,
            user: 0xe358A4Dc52B306b7C7261EaD577B9E140239f2d3,
            mintAmount: 297379679821609960408,
            depositAmount: 605602155708359000000
        });
        entries[780] = MintEntry({
            tokenId: 1009,
            user: 0xE3711ec3a82303419795C6d149Db3CED6C72e16F,
            mintAmount: 191401190847004014038,
            depositAmount: 486881000000000000000
        });
        entries[781] = MintEntry({
            tokenId: 1010,
            user: 0xE386588101bdA66BBADDDCB6E6A716fe3D5dED93,
            mintAmount: 214799314459069579968,
            depositAmount: 484581481599131000000
        });
        entries[782] = MintEntry({
            tokenId: 1011,
            user: 0xe393c2F28A5E7f9e5159CAea972213d760cA0FCA,
            mintAmount: 1586715562121077184611,
            depositAmount: 3331865643749569700000
        });
        entries[783] = MintEntry({
            tokenId: 1013,
            user: 0xe42D09E5E69F9d7c4E303AF570F9EF7F2b5d6d1A,
            mintAmount: 538570158391246240801,
            depositAmount: 1319208190850000000000
        });
        entries[784] = MintEntry({
            tokenId: 1014,
            user: 0xe446Ca4B55EEd81458D241FaA735f34933F037AF,
            mintAmount: 15232312550672797993,
            depositAmount: 36500000000000000000
        });
        entries[785] = MintEntry({
            tokenId: 1015,
            user: 0xE4970dED89570285C247B5e40aC79eC3abb9fe86,
            mintAmount: 480247229497336706193,
            depositAmount: 1160374913140000000000
        });
        entries[786] = MintEntry({
            tokenId: 1016,
            user: 0xE4acA507716AC3804a28f7dFD6bd90c503B7548B,
            mintAmount: 507395347042445977452,
            depositAmount: 1100000000000000000000
        });
        entries[787] = MintEntry({
            tokenId: 1017,
            user: 0xE4cBB2C2F55Ef34F12aA813d288694d48d9B224A,
            mintAmount: 286303370424002208304,
            depositAmount: 606915478113354100000
        });
        entries[788] = MintEntry({
            tokenId: 1018,
            user: 0xe4F28b2D2e4D380C09FEf46d9FEFE5834bF49271,
            mintAmount: 24862138530713634857,
            depositAmount: 500585765849547540000
        });
        entries[789] = MintEntry({
            tokenId: 1019,
            user: 0xe4FA22EcA4fD39b5B96Ecef05cCA1126Bd17Fa4A,
            mintAmount: 78578957002713158165,
            depositAmount: 189751601718216070000
        });
        entries[790] = MintEntry({
            tokenId: 1020,
            user: 0xe5546EA6535859c5d16373ECAbdE6dE89Fb2A4ce,
            mintAmount: 523158619612110423977,
            depositAmount: 1320353747320234000000
        });
        entries[791] = MintEntry({
            tokenId: 1021,
            user: 0xE5a1FbF8Fe438EaAA39884008b9f8Deb6D47e312,
            mintAmount: 194721135172778393024,
            depositAmount: 721731287052500000000
        });
        entries[792] = MintEntry({
            tokenId: 1022,
            user: 0xe5B4F2034ca45390f928087Ef746F72A651D1067,
            mintAmount: 7787872212324055408377,
            depositAmount: 15576715409013124000000
        });
        entries[793] = MintEntry({
            tokenId: 1023,
            user: 0xE5cF553b66cE0daFb2acf1C70E0E8af7232459Cf,
            mintAmount: 4924891143870763109,
            depositAmount: 11000000000000000000
        });
        entries[794] = MintEntry({
            tokenId: 1024,
            user: 0xe5dbFF893E6120C0d013FB046cd755990E4BE9a9,
            mintAmount: 4317034104303908990,
            depositAmount: 10326670317659728000
        });
        entries[795] = MintEntry({
            tokenId: 1026,
            user: 0xE613dF76d94A034aE7282Dfa9f5cA51d2E1E40F5,
            mintAmount: 485482497623056305755,
            depositAmount: 974998046674170000000
        });
        entries[796] = MintEntry({
            tokenId: 1028,
            user: 0xe66D95866d555bf3a2C7e6e2AF233E5F6840B1B0,
            mintAmount: 3403959523089408538,
            depositAmount: 8156642150000000000
        });
        entries[797] = MintEntry({
            tokenId: 1030,
            user: 0xe74166afB1a6c0cA3C355Ba33965a8C7fc3E2616,
            mintAmount: 120350012412824785875,
            depositAmount: 285808903369460400000
        });
        entries[798] = MintEntry({
            tokenId: 1031,
            user: 0xE741f716049dE5514E8304B1C666ee2B18F7027E,
            mintAmount: 57802618370172231637,
            depositAmount: 483406225855199100000
        });
        entries[799] = MintEntry({
            tokenId: 1032,
            user: 0xE77DCDA98BA8839dE3c5F1F627A62F58566DeAe0,
            mintAmount: 8943788830927840880178,
            depositAmount: 25906651509888600000000
        });
        entries[800] = MintEntry({
            tokenId: 1034,
            user: 0xE7d1405C20A23a8e8f9F1BD572d1320c479233EE,
            mintAmount: 172079000928260178139,
            depositAmount: 432472143489378500000
        });
        entries[801] = MintEntry({
            tokenId: 1036,
            user: 0xE7f757cE6160bF0FC0956B00BF9dd89CcA4f0Ead,
            mintAmount: 1558578374570856345550,
            depositAmount: 4219777037257044700000
        });
        entries[802] = MintEntry({
            tokenId: 1037,
            user: 0xe807c33fEf56eFf17e1a3e700ec5A1e14A302868,
            mintAmount: 315803846492931988756,
            depositAmount: 998906740000000000000
        });
        entries[803] = MintEntry({
            tokenId: 1039,
            user: 0xe8342F3F61E8fDB281061A79506Ba4F39ad32c0B,
            mintAmount: 6130828061444329578741,
            depositAmount: 19196322028595940000000
        });
        entries[804] = MintEntry({
            tokenId: 1040,
            user: 0xE85d93Fe753e20Af32b1CB3bb4dEF9B424035a6e,
            mintAmount: 31981343611134446351,
            depositAmount: 86493082320000000000
        });
        entries[805] = MintEntry({
            tokenId: 1042,
            user: 0xe8db873D9D4C9ecB96497B92bA957Bb13AC8CC36,
            mintAmount: 89219427926662346192,
            depositAmount: 213419582951662100000
        });
        entries[806] = MintEntry({
            tokenId: 1043,
            user: 0xe8f57953431F94b9AFC820ca220B25a2849Ae5Aa,
            mintAmount: 138956210470902236270,
            depositAmount: 350000000000000000000
        });
        entries[807] = MintEntry({
            tokenId: 1044,
            user: 0xE9C5f16Ec048Ed0185Dbe6cbD670A2c55670Dc7c,
            mintAmount: 834853483568509580562,
            depositAmount: 1999999987020000000000
        });
        entries[808] = MintEntry({
            tokenId: 1046,
            user: 0xEa3053e144E720EBa39D9e66ECa55a7623efcD81,
            mintAmount: 8743325406571647782,
            depositAmount: 19999991364505000000
        });
        entries[809] = MintEntry({
            tokenId: 1047,
            user: 0xEaC03Ab059b522886A6F273BD96b26bD86a0b4a2,
            mintAmount: 40315980628212279695,
            depositAmount: 101109474343284970000
        });
        entries[810] = MintEntry({
            tokenId: 1049,
            user: 0xEb1Fd48e0BEC6B204A085ccD87B8EdE81d105d81,
            mintAmount: 2177660920379734091,
            depositAmount: 20021350886990000000
        });
        entries[811] = MintEntry({
            tokenId: 1050,
            user: 0xeb4A035aB80e9e95D1167B8E15ad4906e2421586,
            mintAmount: 211500553798063574735,
            depositAmount: 512379911908333500000
        });
        entries[812] = MintEntry({
            tokenId: 1051,
            user: 0xEb8b582Fbdc4E8900a510A4420e24d91097f0e2F,
            mintAmount: 407102579422429227051,
            depositAmount: 1000000000000000000000
        });
        entries[813] = MintEntry({
            tokenId: 1052,
            user: 0xEBb3438C1978E1aA8FF59e89A6e4c3B30B6E765B,
            mintAmount: 310918205258786588782,
            depositAmount: 739821362813976800000
        });
        entries[814] = MintEntry({
            tokenId: 1053,
            user: 0xebedB1973854c8caBfD0Def72Bf1cA38c11D5d99,
            mintAmount: 611151916858986978033,
            depositAmount: 1467579125569538800000
        });
        entries[815] = MintEntry({
            tokenId: 1054,
            user: 0xEc04D7bF52246DBb3850f616d1614F5A509BB6cB,
            mintAmount: 215123872015735500722,
            depositAmount: 458407666707411800000
        });
        entries[816] = MintEntry({
            tokenId: 1056,
            user: 0xEc73833de4b810BB027810Fc8F69f544E83c12D1,
            mintAmount: 67340183548919610971,
            depositAmount: 396873861600000000000
        });
        entries[817] = MintEntry({
            tokenId: 1057,
            user: 0xecA510E9304139De92EDCb64315ee9bd5074d67c,
            mintAmount: 18954445698043622627,
            depositAmount: 50011394913260000000
        });
        entries[818] = MintEntry({
            tokenId: 1058,
            user: 0xECB949c68C825650fD9D0Aebe0cd3796FD126e66,
            mintAmount: 2082177056796892057252,
            depositAmount: 5000000000000000000000
        });
        entries[819] = MintEntry({
            tokenId: 1059,
            user: 0xecCA53828D3CC6DC1FfBdad81ea62C85210a9020,
            mintAmount: 150988362108923362089,
            depositAmount: 347885165970000000000
        });
        entries[820] = MintEntry({
            tokenId: 1061,
            user: 0xECff73ec72ef781F94529f24e89F567ccAb92024,
            mintAmount: 467698387931660542908,
            depositAmount: 1104999439081981200000
        });
        entries[821] = MintEntry({
            tokenId: 1062,
            user: 0xed02f16a57c32a08b55d923Bf4690D200722f462,
            mintAmount: 818688450357872203363,
            depositAmount: 3000000000000000000000
        });
        entries[822] = MintEntry({
            tokenId: 1063,
            user: 0xeD1fEcbA8530a0f90d26bfb8a0D27C2d66aD6889,
            mintAmount: 189079961630982859757,
            depositAmount: 513400567767622800000
        });
        entries[823] = MintEntry({
            tokenId: 1064,
            user: 0xEd963afEd4188993754c045f2F7055d19A7a9DA6,
            mintAmount: 351243000062923930382,
            depositAmount: 828184243490000000000
        });
        entries[824] = MintEntry({
            tokenId: 1065,
            user: 0xEE24487be049Adf2D7b2c932150848B9bC47E931,
            mintAmount: 221828599975962724416,
            depositAmount: 600228493964823800000
        });
        entries[825] = MintEntry({
            tokenId: 1066,
            user: 0xEE8e0FcC8bFF03Ec5f100D02Cb7b3196D78863a7,
            mintAmount: 4522767404549666026,
            depositAmount: 22335849159106120000
        });
        entries[826] = MintEntry({
            tokenId: 1067,
            user: 0xeE9AE5Bdc43aC8e0Cb1168A99Eb7fa1684043Ae0,
            mintAmount: 2481394505251847425998,
            depositAmount: 7062422655906651000000
        });
        entries[827] = MintEntry({
            tokenId: 1069,
            user: 0xEEf167abC7Ce5b85C4f3A676E0fE4B706c7b3d33,
            mintAmount: 381830395880360330449,
            depositAmount: 910621597149814600000
        });
        entries[828] = MintEntry({
            tokenId: 1070,
            user: 0xeF6392bee592DA98166a14565AB939aB7294543D,
            mintAmount: 34947519086624024929,
            depositAmount: 88898522340000000000
        });
        entries[829] = MintEntry({
            tokenId: 1072,
            user: 0xF0573bb8fD4AbAE0a3E539b1B44EAEfE2E3cA2f9,
            mintAmount: 177873985424467094161,
            depositAmount: 530214539935704940000
        });
        entries[830] = MintEntry({
            tokenId: 1073,
            user: 0xf075590c7ea5700F8Cc34507f39D02d483167066,
            mintAmount: 3249791706417251362846,
            depositAmount: 6623163752261503000000
        });
        entries[831] = MintEntry({
            tokenId: 1074,
            user: 0xF0eC03d131f9e5Ca29638fad253e874e63Dd9865,
            mintAmount: 898106002070515201175,
            depositAmount: 2345000000000000000000
        });
        entries[832] = MintEntry({
            tokenId: 1075,
            user: 0xF1B96fAf44D0a04F7A39ed90b4B3A2942403b109,
            mintAmount: 145972473621899868944,
            depositAmount: 349935455709000000000
        });
        entries[833] = MintEntry({
            tokenId: 1076,
            user: 0xf1DFbC7341f641c2FBE9861D2566af4D89801f6e,
            mintAmount: 57145742652736555975728,
            depositAmount: 210160333979380250000000
        });
        entries[834] = MintEntry({
            tokenId: 1078,
            user: 0xF262FcD1262Cec8B86ab9d9F34a7A2b7FF762D94,
            mintAmount: 226675158632971208808,
            depositAmount: 531967791539398300000
        });
        entries[835] = MintEntry({
            tokenId: 1079,
            user: 0xf2643e655B01355ACCB09F781F90CC46c8b066dF,
            mintAmount: 18421286644823247684,
            depositAmount: 44141489370000000000
        });
        entries[836] = MintEntry({
            tokenId: 1080,
            user: 0xf2662D8ebC90e92CE585596acAB5143aBd42A284,
            mintAmount: 208089217128043640929,
            depositAmount: 500000000000000000000
        });
        entries[837] = MintEntry({
            tokenId: 1081,
            user: 0xF26f920dB2aF3613366a2bcE15e5470a312EABf5,
            mintAmount: 29683177902984771498,
            depositAmount: 70612503141269620000
        });
        entries[838] = MintEntry({
            tokenId: 1082,
            user: 0xF2BE965264FBF526b13962af43170aA9e42a6296,
            mintAmount: 179561821311262059624,
            depositAmount: 400000000000000000000
        });
        entries[839] = MintEntry({
            tokenId: 1083,
            user: 0xf2Fa78D7fD9D50d4C59042B51fF18e6BA4d72B9F,
            mintAmount: 3290003017900325687499,
            depositAmount: 9978686709145815000000
        });
        entries[840] = MintEntry({
            tokenId: 1084,
            user: 0xF3dF14b24e982DF7C0943d4B4DdeBf18a23240eB,
            mintAmount: 2459107824513709450642,
            depositAmount: 6000000000000000000000
        });
        entries[841] = MintEntry({
            tokenId: 1085,
            user: 0xf43257DF6B2066C866ceee61218ee1Ee50D3be6f,
            mintAmount: 3223525963776907893811,
            depositAmount: 9999741963876140000000
        });
        entries[842] = MintEntry({
            tokenId: 1087,
            user: 0xF55Dd2ae6B87C1e4B754706C98a3a204C3D98C64,
            mintAmount: 520821386636340591257,
            depositAmount: 1200000000000000000000
        });
        entries[843] = MintEntry({
            tokenId: 1088,
            user: 0xf57c1A05e4C512275650f75AD2B8074700017F0B,
            mintAmount: 112173041356034296969,
            depositAmount: 249983345694655900000
        });
        entries[844] = MintEntry({
            tokenId: 1090,
            user: 0xF6030b263C14ae3DEd0Afd41b73644921B8a75Fb,
            mintAmount: 2476845391347482010358,
            depositAmount: 5307795790297065000000
        });
        entries[845] = MintEntry({
            tokenId: 1093,
            user: 0xf74b4176F79669255EF6746D4F4b60E78CE4a5b4,
            mintAmount: 2686359048347745197686,
            depositAmount: 10000000000000000000000
        });
        entries[846] = MintEntry({
            tokenId: 1095,
            user: 0xF7c94fb69150A643d39B24c3d5f1a6cd10Fc3728,
            mintAmount: 391498684413240738522,
            depositAmount: 983921770280685000000
        });
        entries[847] = MintEntry({
            tokenId: 1096,
            user: 0xF7D3498612104A25D8A6E271441e0e9fb24d224D,
            mintAmount: 394060476476890102990,
            depositAmount: 996728150000000000000
        });
        entries[848] = MintEntry({
            tokenId: 1097,
            user: 0xF7Ecba7624F3BeF5b4CcacdC038EE041BdE8feDC,
            mintAmount: 222171939368760751692,
            depositAmount: 652072104138526800000
        });
        entries[849] = MintEntry({
            tokenId: 1099,
            user: 0xf824DE6Fa90fCaBe1F9E44B67B7AB02C89c3D216,
            mintAmount: 984203529000778971107,
            depositAmount: 2500000000000000000000
        });
        entries[850] = MintEntry({
            tokenId: 1100,
            user: 0xf8483AC6f76F02E476Cd466d3707dC6842f9F217,
            mintAmount: 146555009964412781154,
            depositAmount: 348901650847472300000
        });
        entries[851] = MintEntry({
            tokenId: 1102,
            user: 0xf878b5c583bad66F57E2e0F0e9c674542a3c8b5c,
            mintAmount: 259180629437394849930,
            depositAmount: 701296401315789400000
        });
        entries[852] = MintEntry({
            tokenId: 1104,
            user: 0xF8845DC5d67D0bfbde9e9D2E3D274B4500FeD9Ad,
            mintAmount: 136256302626371248910,
            depositAmount: 315787277632882100000
        });
        entries[853] = MintEntry({
            tokenId: 1105,
            user: 0xf8DAbB428c19f20D8c6b10e21F7D38fe4caAd719,
            mintAmount: 13118278478764206893,
            depositAmount: 29999559892845703000
        });
        entries[854] = MintEntry({
            tokenId: 1106,
            user: 0xf8Ee872652e2B8AE594E6a3F83048F5704114658,
            mintAmount: 4394039741021407115865,
            depositAmount: 16432651447128178000000
        });
        entries[855] = MintEntry({
            tokenId: 1108,
            user: 0xf9224b2a7044563189eA40dCC351790283736794,
            mintAmount: 1844242462159028244692,
            depositAmount: 4036118816410000000000
        });
        entries[856] = MintEntry({
            tokenId: 1109,
            user: 0xf94aAA667ea9934a13c09ae932428E2d71B06678,
            mintAmount: 61139051899337292735,
            depositAmount: 130917269425736480000
        });
        entries[857] = MintEntry({
            tokenId: 1110,
            user: 0xF9605D8c4c987d7Cb32D0d11FbCb8EeeB1B22D5d,
            mintAmount: 7425652785408049061,
            depositAmount: 19999982729010000000
        });
        entries[858] = MintEntry({
            tokenId: 1111,
            user: 0xF9Ca61b2C3938D3C5Ec8Fa669622240A7a0cb316,
            mintAmount: 398918428640900905053,
            depositAmount: 1000000000000000000000
        });
        entries[859] = MintEntry({
            tokenId: 1112,
            user: 0xfA8D867c6E0ECC4f1fbD131ad1A471EfA1bb0E49,
            mintAmount: 35716135353467077758,
            depositAmount: 79595229861018200000
        });
        entries[860] = MintEntry({
            tokenId: 1114,
            user: 0xFB0D01283e5b668D67c3788DC9Fc3394451951db,
            mintAmount: 89266482455819837128,
            depositAmount: 240790390000000000000
        });
        entries[861] = MintEntry({
            tokenId: 1115,
            user: 0xfb0f37C0456d60eDEd9b64442dFB0C4847CdD06A,
            mintAmount: 277299070619101567433,
            depositAmount: 755340204566713300000
        });
        entries[862] = MintEntry({
            tokenId: 1117,
            user: 0xFb2c9a817c1c347c0164a8211CF7014650379cfa,
            mintAmount: 1359580309832424367,
            depositAmount: 3661554686048875000
        });
        entries[863] = MintEntry({
            tokenId: 1119,
            user: 0xfB98168d6A622124a14C1f3D3556E825bfE3a264,
            mintAmount: 36499824916881782015,
            depositAmount: 98817436375225430000
        });
        entries[864] = MintEntry({
            tokenId: 1120,
            user: 0xFbf0e5d8219fa45c8fCf6eA6e9Ac17beE9488513,
            mintAmount: 2883430184305175324285,
            depositAmount: 6042149325581189000000
        });
        entries[865] = MintEntry({
            tokenId: 1121,
            user: 0xFbF51b2ee5A657bA1C7D0741dd31156f2a4A942A,
            mintAmount: 82547346919839708226,
            depositAmount: 224953418587659300000
        });
        entries[866] = MintEntry({
            tokenId: 1122,
            user: 0xfC44E9e484bd782e7b3414D6180f898DFa051b36,
            mintAmount: 37817485838688583301,
            depositAmount: 151097171599833240000
        });
        entries[867] = MintEntry({
            tokenId: 1123,
            user: 0xFC5Cb08372D5E47b1ded91279616D195F67f5aA5,
            mintAmount: 26549755449782289584,
            depositAmount: 62151269380000000000
        });
        entries[868] = MintEntry({
            tokenId: 1124,
            user: 0xFca32B89d0981e69C8dadCDcc0668b0E01c810CF,
            mintAmount: 37041394406252092505,
            depositAmount: 100000000000000000000
        });
        entries[869] = MintEntry({
            tokenId: 1125,
            user: 0xFCcb964C514C12794509ed62fa274f0E284ceE82,
            mintAmount: 1410862067918879170742,
            depositAmount: 3474244560000000000000
        });
        entries[870] = MintEntry({
            tokenId: 1126,
            user: 0xfCDF138316302049599D629146C253b08bB3B449,
            mintAmount: 3001044265178975829,
            depositAmount: 6421925835087759000
        });
        entries[871] = MintEntry({
            tokenId: 1127,
            user: 0xFD0460BCE7BEf3436f99cDf7F714FF39DB12a273,
            mintAmount: 215962831844596443417,
            depositAmount: 512649394400000000000
        });
        entries[872] = MintEntry({
            tokenId: 1129,
            user: 0xfDcB736d927C0D51F7b7662e4C8098768Cd87345,
            mintAmount: 104509493313247614011,
            depositAmount: 250000000000000000000
        });
        entries[873] = MintEntry({
            tokenId: 1130,
            user: 0xFE4E4B5C7Ae92008EdF477A80c0de1D6cD4fad54,
            mintAmount: 168402937470946947244,
            depositAmount: 392860541594728900000
        });
        entries[874] = MintEntry({
            tokenId: 1131,
            user: 0xfE5fE702d9667B3c36f3c330151273B0eD71FE04,
            mintAmount: 209967315788320893727,
            depositAmount: 501531191350423900000
        });
        entries[875] = MintEntry({
            tokenId: 1132,
            user: 0xFE91BB5176f645Cdb34d5a03c3F5aa6F4629e141,
            mintAmount: 386924804965853618241,
            depositAmount: 1100751157205731400000
        });
        entries[876] = MintEntry({
            tokenId: 1133,
            user: 0xFEE73F35e5E162bB687452447b73aA2dA5670226,
            mintAmount: 16952763867420245562,
            depositAmount: 98983784700000000000
        });
        entries[877] = MintEntry({
            tokenId: 1134,
            user: 0xfeEcBbFD59EfA65cAB480a1853df869099030108,
            mintAmount: 197602862995920244825,
            depositAmount: 521505092542509350000
        });
        entries[878] = MintEntry({
            tokenId: 1138,
            user: 0xFFaaf10a141C03a9BAf4362B843CAdf9dd3fF41f,
            mintAmount: 3739667403252780279,
            depositAmount: 19999972349098000000
        });
        entries[879] = MintEntry({
            tokenId: 1139,
            user: 0xFFfA527Ab78daB60437C3809F3218Cb2B71342D2,
            mintAmount: 1629382397923153546291,
            depositAmount: 4462546954813288000000
        });

        return entries;
    }
}
