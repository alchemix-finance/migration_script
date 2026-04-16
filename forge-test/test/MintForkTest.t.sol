// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "./MintData.sol";

interface IAlchemistV3 {
    function mint(uint256 tokenId, uint256 amount, address recipient) external;
}

contract MintForkTest is Test {
    address constant ALCHEMIST = 0xeB83112d925268BeDe86654C13D423a987587e3E;
    address constant MULTISIG = 0xF56D660138815fC5d7a06cd0E1630225E788293D;

    IAlchemistV3 alchemist;

    function setUp() public {
        alchemist = IAlchemistV3(ALCHEMIST);
    }

    function test_mintBatch1() public { _mintRange(0, 200); }
    function test_mintBatch2() public { _mintRange(200, 400); }
    function test_mintBatch3() public { _mintRange(400, 600); }
    function test_mintBatch4() public { _mintRange(600, 800); }
    function test_mintBatch5() public { _mintRange(800, 880); }

    function _mintRange(uint256 start, uint256 end) internal {
        MintEntry[] memory entries = MintData.getEntries();
        require(end <= entries.length, "out of bounds");

        uint256 successCount;
        uint256 failCount;

        for (uint256 i = start; i < end; i++) {
            MintEntry memory e = entries[i];

            vm.prank(MULTISIG);
            try alchemist.mint(e.tokenId, e.mintAmount, e.user) {
                successCount++;
            } catch Error(string memory reason) {
                emit log_named_string("REVERT", reason);
                emit log_named_uint("  index", i);
                emit log_named_uint("  tokenId", e.tokenId);
                emit log_named_uint("  mintAmount", e.mintAmount);
                emit log_named_address("  user", e.user);
                failCount++;
            } catch (bytes memory) {
                emit log_named_string("REVERT (raw)", "no reason");
                emit log_named_uint("  index", i);
                emit log_named_uint("  tokenId", e.tokenId);
                emit log_named_uint("  mintAmount", e.mintAmount);
                emit log_named_address("  user", e.user);
                failCount++;
            }
        }

        emit log_named_uint("Batch successes", successCount);
        emit log_named_uint("Batch failures", failCount);
        assertEq(failCount, 0, "Some mint calls failed in batch");
    }
}
