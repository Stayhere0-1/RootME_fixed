-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 05, 2025 at 07:31 AM
-- Server version: 10.4.32-MariaDB-log
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rootme_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `kategori_soal`
--

CREATE TABLE `kategori_soal` (
  `Kategori_id` int(11) NOT NULL,
  `Kategori_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `kategori_soal`
--

INSERT INTO `kategori_soal` (`Kategori_id`, `Kategori_name`) VALUES
(1, 'Blockchain'),
(2, 'Web Exploitation'),
(3, 'Reverse Enginering'),
(4, 'Misc'),
(5, 'Cryptography'),
(6, 'PWN'),
(7, 'Forensic'),
(8, 'Mobile');

-- --------------------------------------------------------

--
-- Table structure for table `leaderboard`
--

CREATE TABLE `leaderboard` (
  `ID` int(11) NOT NULL,
  `Total_Point` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `leaderboard`
--

INSERT INTO `leaderboard` (`ID`, `Total_Point`) VALUES
(25, 1000);

-- --------------------------------------------------------

--
-- Table structure for table `soal`
--

CREATE TABLE `soal` (
  `Soal_id` int(11) NOT NULL,
  `Kategori_id` int(11) DEFAULT NULL,
  `Soal_name` varchar(50) DEFAULT NULL,
  `Soal_Isi` varchar(256) DEFAULT NULL,
  `Attachment` varchar(50) DEFAULT NULL,
  `Koneksi_Info` varchar(50) DEFAULT NULL,
  `Value` int(11) DEFAULT NULL,
  `flag` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `soal`
--

INSERT INTO `soal` (`Soal_id`, `Kategori_id`, `Soal_name`, `Soal_Isi`, `Attachment`, `Koneksi_Info`, `Value`, `flag`) VALUES
(2, 6, 'ALA', '-', '-', '-', 1000, 'AKUNAIM'),
(3, 6, 'ALO', '-', '-', '-', 200, 'AB'),
(4, 6, 'aa', '-', '-', '-', 200, '100'),
(6, 2, 'HTML', '-', '-', '-', 12, '-'),
(9, 5, 'SETDOWN', 'LOW FREKUESI coba A+1 =?', '', '', 1000, 'B');

-- --------------------------------------------------------

--
-- Table structure for table `submit`
--

CREATE TABLE `submit` (
  `Submit_ID` int(11) NOT NULL,
  `ID` int(11) DEFAULT NULL,
  `Soal_ID` int(11) DEFAULT NULL,
  `Record_Submit` varchar(256) DEFAULT NULL,
  `Benar_Salah` enum('Benar','Salah') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `submit`
--

INSERT INTO `submit` (`Submit_ID`, `ID`, `Soal_ID`, `Record_Submit`, `Benar_Salah`) VALUES
(24, 25, 9, 'B', 'Benar');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `ID` int(11) NOT NULL,
  `Username` varchar(256) DEFAULT NULL,
  `Mail` varchar(256) DEFAULT NULL,
  `Password_md5` varchar(256) DEFAULT NULL,
  `Role` enum('Admin','Player') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`ID`, `Username`, `Mail`, `Password_md5`, `Role`) VALUES
(21, 'HAXOR_GAMING', 'malikdayat1207@gmail.com', 'b420c7292278c366ded49ab615a2af9c', 'Admin'),
(22, 'MAUL1234', 'maliksaya3@gmail.com', '8d749919f56d2d6a439fd67176ba3442', 'Player'),
(23, 'MAUL12345', 'masopole@gmail.com', '4677d79d4502e8d1cdcfb63c51f8ae05', 'Player'),
(24, 'TEST1234', 'maul@gmail.com', '2aaf1f597c85a93d49646e8532e2072a', 'Player'),
(25, 'Namikaz3', 'azka.naim0103@gmail.com', '6ffc61306d737540a8f5bec1677e5eb1', 'Player');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `kategori_soal`
--
ALTER TABLE `kategori_soal`
  ADD PRIMARY KEY (`Kategori_id`);

--
-- Indexes for table `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `soal`
--
ALTER TABLE `soal`
  ADD PRIMARY KEY (`Soal_id`),
  ADD KEY `Kategori_id` (`Kategori_id`);

--
-- Indexes for table `submit`
--
ALTER TABLE `submit`
  ADD PRIMARY KEY (`Submit_ID`),
  ADD KEY `submit_ibfk_1` (`ID`),
  ADD KEY `submit_ibfk_2` (`Soal_ID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `kategori_soal`
--
ALTER TABLE `kategori_soal`
  MODIFY `Kategori_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `soal`
--
ALTER TABLE `soal`
  MODIFY `Soal_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `submit`
--
ALTER TABLE `submit`
  MODIFY `Submit_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD CONSTRAINT `leaderboard_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `user` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `soal`
--
ALTER TABLE `soal`
  ADD CONSTRAINT `soal_ibfk_1` FOREIGN KEY (`Kategori_id`) REFERENCES `kategori_soal` (`Kategori_id`);

--
-- Constraints for table `submit`
--
ALTER TABLE `submit`
  ADD CONSTRAINT `submit_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `user` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `submit_ibfk_2` FOREIGN KEY (`Soal_ID`) REFERENCES `soal` (`Soal_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
